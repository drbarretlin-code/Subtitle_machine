import os
import asyncio
import json
import uuid
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from backend.audio_engine import audio_engine
from backend.subtitle_engine import subtitle_engine
from backend.chunker import VADChunker

app = FastAPI()

class SubtitleCoordinator:
    def __init__(self):
        self.context_history = collections.deque(maxlen=5)

    async def process_segment(self, websocket, audio_data, config):
        try:
            # 1. ASR 辨識
            input_lang = None if config["inputLang"] == "auto" else config["inputLang"]
            raw_text, lang = await audio_engine.transcribe(audio_data, input_lang)
            
            if not raw_text.strip() or len(raw_text) < 2:
                return

            print(f"🎤 ASR: [{raw_text}]")
            
            # 2. 翻譯與校正
            context_str = " | ".join(self.context_history)
            refined_text = await subtitle_engine.refine_text(
                raw_text, 
                context=context_str, 
                target_lang=config["targetLang"]
            )
            
            print(f"✨ 翻譯: [{refined_text}]")
            
            # 3. 更新上下文並發送
            self.context_history.append(refined_text)
            
            await websocket.send_json({
                "id": str(uuid.uuid4()),
                "raw": raw_text,
                "refined": refined_text,
                "language": lang,
                "timestamp": asyncio.get_event_loop().time()
            })
            
        except Exception as e:
            print(f"❌ 處理片段失敗: {e}")

import collections

@app.websocket("/ws/audio")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🔌 WebSocket 已連接 (進階架構)")
    
    chunker = VADChunker()
    coordinator = SubtitleCoordinator()
    current_config = {"inputLang": "auto", "targetLang": "繁體中文"}
    
    try:
        while True:
            message = await websocket.receive()
            
            if message.get("type") == "websocket.disconnect":
                break

            if "text" in message:
                data = json.loads(message["text"])
                if data.get("type") == "config":
                    current_config.update(data)
                continue
            
            if "bytes" in message:
                audio_chunk = np.frombuffer(message["bytes"], dtype=np.float32)
                chunker.add_audio(audio_chunk)
                
                # 取得可處理的音訊段
                segment = chunker.get_next_segment()
                if segment is not None:
                    # 非同步處理，不阻塞接收循環
                    asyncio.create_task(coordinator.process_segment(websocket, segment, current_config))

    except WebSocketDisconnect:
        print("❌ WebSocket 已斷開")
    except Exception as e:
        print(f"‼️ WebSocket 錯誤: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
