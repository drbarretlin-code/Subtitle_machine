import numpy as np
import collections

class VADChunker:
    def __init__(self, sample_rate=16000, chunk_size_ms=30):
        self.sample_rate = sample_rate
        self.chunk_size = int(sample_rate * chunk_size_ms / 1000)
        self.buffer = np.array([], dtype=np.float32)
        
    def add_audio(self, audio_chunk: np.ndarray):
        self.buffer = np.concatenate([self.buffer, audio_chunk])
        
    def get_next_segment(self, min_duration=5, max_duration=15):
        """
        嘗試從 Buffer 中切出一段音訊。
        目前簡單實作：若滿 5 秒則切出，或達到 15 秒強制切出。
        未來可串接 Silero VAD 進行精確停頓切分。
        """
        samples_min = self.sample_rate * min_duration
        samples_max = self.sample_rate * max_duration
        
        if len(self.buffer) >= samples_max:
            segment = self.buffer[:samples_max]
            self.buffer = self.buffer[samples_max:] # 無重疊切分，或可保留少量重疊
            return segment
            
        # 如果有足夠長度且偵測到靜音（暫以能量判斷）
        if len(self.buffer) >= samples_min:
            # 簡單能量偵測
            recent_energy = np.mean(np.abs(self.buffer[-1600:])) # 最後 100ms
            if recent_energy < 0.01:
                segment = self.buffer
                self.buffer = np.array([], dtype=np.float32)
                return segment
                
        return None
