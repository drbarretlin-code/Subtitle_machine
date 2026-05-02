import os
import io
import numpy as np
import torch
import asyncio
from typing import Tuple, Optional
from faster_whisper import WhisperModel
from groq import Groq
from backend.key_manager import key_manager
import wave

# 設定
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")
DEVICE = "cpu"
COMPUTE_TYPE = "int8"

class AudioEngine:
    def __init__(self):
        print(f"📦 初始化 ASR 引擎 (模型: {WHISPER_MODEL_SIZE})...")
        # 本地模型
        self.local_model = WhisperModel(WHISPER_MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
        
        # VAD 模型 (Silero)
        self.vad_model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad', model='silero_vad', force_reload=False)
        (self.get_speech_timestamps, _, _, _, _) = utils
        
    def _to_wav_bytes(self, audio_data: np.ndarray, sample_rate: int = 16000) -> bytes:
        """將 numpy array 轉換為 WAV 位元組供 API 使用"""
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2) # 16-bit
            wf.setframerate(sample_rate)
            # 轉換 float32 為 int16
            audio_int16 = (audio_data * 32767).astype(np.int16)
            wf.writeframes(audio_int16.tobytes())
        return buf.getvalue()

    async def transcribe_cloud(self, audio_data: np.ndarray, language: Optional[str] = None) -> Optional[str]:
        """嘗試使用 Groq Cloud ASR"""
        api_key = key_manager.get_groq_key()
        if not api_key:
            return None
        
        try:
            client = Groq(api_key=api_key)
            wav_bytes = self._to_wav_bytes(audio_data)
            
            # 呼叫 Groq Whisper
            # Groq API 目前需要檔案形式
            response = await asyncio.to_thread(
                client.audio.transcriptions.create,
                file=("audio.wav", wav_bytes),
                model="whisper-large-v3",
                language=language,
                response_format="text"
            )
            return response
        except Exception as e:
            print(f"❌ Groq ASR 失敗: {e}")
            if "429" in str(e):
                key_manager.report_error(api_key, "groq", 429)
            return None

    def transcribe_local(self, audio_data: np.ndarray, language: Optional[str] = None) -> Tuple[str, str]:
        """本機 ASR 備援"""
        segments, info = self.local_model.transcribe(
            audio_data,
            beam_size=1,
            language=language,
            vad_filter=True
        )
        text = "".join([s.text for s in segments])
        return text, info.language

    async def transcribe(self, audio_data: np.ndarray, language: Optional[str] = None) -> Tuple[str, str]:
        """混合式 ASR 流程"""
        # 1. 嘗試雲端
        cloud_text = await self.transcribe_cloud(audio_data, language)
        if cloud_text:
            print("🚀 [Cloud] ASR 辨識成功")
            return cloud_text.strip(), language or "auto"
        
        # 2. 雲端失敗，降級至本機
        print("🏠 [Local] 執行本機備援辨識")
        return self.transcribe_local(audio_data, language)

# 全域單例
audio_engine = AudioEngine()
