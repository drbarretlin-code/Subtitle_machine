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

    async def refine_text(self, raw_text, language="auto", target_lang="繁體中文"):
        """使用 Gemini 1.5 Flash 進行口音校正與目標語系翻譯"""
        if not self.gemini_client or not raw_text.strip():
            return raw_text

        prompt = (
            f"你是一位專業的即時字幕翻譯與校對專家。\n"
            f"當前偵測語系: {language}\n"
            f"目標輸出語系: {target_lang}\n\n"
            f"任務:\n"
            f"1. 修正原始辨識錯誤 (ASR 錯誤)。\n"
            f"2. 將內容翻譯/優化為「{target_lang}」。\n"
            f"3. 語氣要自然、流暢、簡潔，適合做為直播字幕。\n"
            f"4. 僅輸出修正或翻譯後的內容，不要任何解釋。\n\n"
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

    def transcribe(self, audio_data, language=None):
        """執行 ASR 辨識"""
        # 指定 language 可提升特定語系的辨識率與速度
        segments, info = whisper_model.transcribe(audio_data, beam_size=5, language=language)
        text = "".join([s.text for s in segments])
        return text, info.language

engine = SubtitleEngine(gemini_model)

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket 已連接")
    
    audio_buffer = []
    current_config = {"inputLang": "auto", "targetLang": "繁體中文"}
    
    try:
        while True:
            # 接收數據 (可能是 JSON 或 Bytes)
            message = await websocket.receive()
            
            if "text" in message:
                import json
                data = json.loads(message["text"])
                if data.get("type") == "config":
                    current_config.update(data)
                continue
            
            if "bytes" in message:
                audio_chunk = np.frombuffer(message["bytes"], dtype=np.float32)
                audio_buffer.append(audio_chunk)

            # 當緩衝累積到一定量進行 VAD 與辨識
            if len(audio_buffer) >= 10: # 約 1.2 秒
                full_audio = np.concatenate(audio_buffer)
                
                # VAD 偵測
                audio_tensor = torch.from_numpy(full_audio)
                speech_timestamps = get_speech_timestamps(audio_tensor, vad_model, sampling_rate=16000)
                
                # 觸發辨識
                if len(audio_buffer) >= 15: # 約 2 秒
                    raw_audio = np.concatenate(audio_buffer)
                    print(f"正在辨識音訊 (長度: {len(raw_audio)} samples)...")
                    
                    # 使用設定的輸入語系
                    input_lang = None if current_config["inputLang"] == "auto" else current_config["inputLang"]
                    text, lang = engine.transcribe(raw_audio, language=input_lang)
                    
                    if text.strip():
                        print(f"辨識結果: {text} ({lang})")
                        # 傳入目標語系進行校正與翻譯
                        refined_text = await engine.refine_text(text, lang, target_lang=current_config["targetLang"])
                        print(f"Gemini 校正: {refined_text}")
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
