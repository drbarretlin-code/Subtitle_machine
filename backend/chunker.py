import numpy as np
import collections

class VADChunker:
    def __init__(self, sample_rate=16000, chunk_size_ms=30):
        self.sample_rate = sample_rate
        self.chunk_size = int(sample_rate * chunk_size_ms / 1000)
        self.buffer = np.array([], dtype=np.float32)
        
    def add_audio(self, audio_chunk: np.ndarray):
        self.buffer = np.concatenate([self.buffer, audio_chunk])
        
    def get_next_segment(self, min_duration=2.5, max_duration=5.0):
        """
        嘗試從 Buffer 中切出一段音訊。
        新增能量檢查：若整段音訊能量過低，直接捨棄以節省 API 額度。
        """
        samples_min = int(self.sample_rate * min_duration)
        samples_max = int(self.sample_rate * max_duration)
        
        if len(self.buffer) < samples_min:
            return None

        # 計算整段能量
        total_energy = np.mean(np.abs(self.buffer[:samples_min]))
        if total_energy < 0.005: # 門檻值：過低代表純雜訊或安靜
            self.buffer = self.buffer[samples_min:]
            return None

        if len(self.buffer) >= samples_max:
            segment = self.buffer[:samples_max]
            self.buffer = self.buffer[samples_max:]
            return segment
            
        # 偵測結尾停頓
        recent_energy = np.mean(np.abs(self.buffer[-1600:]))
        if recent_energy < 0.008:
            segment = self.buffer
            self.buffer = np.array([], dtype=np.float32)
            return segment
                
        return None
