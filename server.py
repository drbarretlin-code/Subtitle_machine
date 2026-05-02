import os
import asyncio
import numpy as np
import torch
import google.generativeai as genai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from faster_whisper import WhisperModel
from dotenv import load_dotenv

load_dotenv()

# --- 配置 ---
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("VITE_GEMINI_KEY")
WHISPER_MODEL_SIZE = "base"  # 可改為 'large-v3' 以提升精度
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
COMPUTE_TYPE = "float16" if DEVICE == "cuda" else "int8"

# 初始化 Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-1.5-flash')
else:
    print("警告: 未偵測到 GOOGLE_API_KEY，校正功能將失效。")
    gemini_model = None

# 初始化 Whisper
print(f"正在載入 Whisper 模型 ({WHISPER_MODEL_SIZE}) 於 {DEVICE}...")
whisper_model = WhisperModel(WHISPER_MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)

# 初始化 Silero VAD
print("正在載入 Silero VAD 模型...")
vad_model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False)
(get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = utils

app = FastAPI()

class SubtitleEngine:
    def __init__(self, gemini_client):
        self.gemini_client = gemini_client

    async def refine_text(self, raw_text, language="auto"):
        """使用 Gemini 1.5 Flash 進行口音校正與語法優化"""
        if not self.gemini_client or not raw_text.strip():
            return raw_text

        prompt = (
            f"你是一位專業的即時字幕翻譯與校對專家。輸入的文字是從語音辨識 (ASR) 產生，可能包含口音導致的錯誤或雜訊。\n"
            f"當前語系: {language}\n"
            f"任務:\n"
            f"1. 修正明顯的辨識錯誤（特別是針對泰、印、越、馬、日、韓口音的英文或原生語系）。\n"
            f"2. 使語言自然流暢，適合做為直播字幕。\n"
            f"3. 保持語意不變，僅輸出修正後的文字，不要包含任何解釋。\n\n"
            f"原始文字: {raw_text}"
        )

        try:
            response = await asyncio.to_thread(
                self.gemini_client.generate_content, 
                prompt
            )
            return response.text.strip()
        except Exception as e:
            print(f"Gemini 校正失敗: {e}")
            return raw_text

    def transcribe(self, audio_data):
        """執行 ASR 辨識"""
        segments, info = whisper_model.transcribe(audio_data, beam_size=5)
        text = "".join([s.text for s in segments])
        return text, info.language

engine = SubtitleEngine(gemini_model)

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket 已連接")
    
    audio_buffer = []
    # 採集參數: 16000Hz, 單聲道
    # 前端傳送的資料應為 Float32 的 Raw Audio
    
    try:
        while True:
            # 接收前端傳來的音訊 Chunk (binary)
            data = await websocket.receive_bytes()
            audio_chunk = np.frombuffer(data, dtype=np.float32)
            audio_buffer.append(audio_chunk)

            # 當緩衝累積到一定長度 (例如 1 秒) 進行 VAD 檢查
            if len(audio_buffer) >= 20: # 假設前端每 50ms 傳送一個 chunk
                full_audio = np.concatenate(audio_buffer)
                
                # VAD 偵測
                audio_tensor = torch.from_numpy(full_audio)
                speech_timestamps = get_speech_timestamps(audio_tensor, vad_model, sampling_rate=16000)
                
                # 如果偵測到說話結束或長時間停頓，則觸發辨識
                # 這裡簡化邏輯：如果有聲音且緩衝足夠長，或偵測到靜音
                if len(speech_timestamps) > 0:
                    # 模擬處理：實際應用中應更細緻地判斷 Segment 結束
                    pass

                # 目前採取的策略：每 3 秒觸發一次辨識 (或根據 VAD 切割)
                if len(audio_buffer) >= 60: # 約 3 秒
                    raw_audio = np.concatenate(audio_buffer)
                    text, lang = engine.transcribe(raw_audio)
                    
                    if text.strip():
                        refined_text = await engine.refine_text(text, lang)
                        await websocket.send_json({
                            "raw": text,
                            "refined": refined_text,
                            "language": lang
                        })
                    
                    audio_buffer = [] # 重置緩衝區

    except WebSocketDisconnect:
        print("WebSocket 已斷開")
    except Exception as e:
        print(f"錯誤: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
