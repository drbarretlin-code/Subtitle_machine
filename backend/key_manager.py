import os
import time
import asyncio
from typing import List, Dict, Optional
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class APIKey:
    def __init__(self, key: str, service: str):
        self.key = key
        self.service = service # 'gemini' or 'groq'
        self.cooldown_until = 0
        self.rpm_count = 0
        self.last_reset = time.time()
        
    def is_available(self) -> bool:
        return time.time() > self.cooldown_until

    def set_cooldown(self, seconds: int = 60):
        self.cooldown_until = time.time() + seconds
        print(f"⚠️ {self.service} 金鑰進入冷卻期 ({seconds}秒)")

class KeyManager:
    def __init__(self):
        self.gemini_keys: List[APIKey] = []
        self.groq_keys: List[APIKey] = []
        self._load_keys()
        
        self.current_gemini_idx = 0
        self.current_groq_idx = 0

    def _load_keys(self):
        # Gemini Keys
        g_keys = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY")
        if g_keys:
            for k in g_keys.split(","):
                if k.strip():
                    self.gemini_keys.append(APIKey(k.strip(), "gemini"))
        
        # Groq Keys
        gr_keys = os.getenv("GROQ_API_KEYS") or os.getenv("GROQ_API_KEY")
        if gr_keys:
            for k in gr_keys.split(","):
                if k.strip():
                    self.groq_keys.append(APIKey(k.strip(), "groq"))

        print(f"✅ 已載入 {len(self.gemini_keys)} 組 Gemini 金鑰, {len(self.groq_keys)} 組 Groq 金鑰")

    def get_gemini_key(self) -> Optional[str]:
        if not self.gemini_keys:
            return None
        
        start_idx = self.current_gemini_idx
        while True:
            key_obj = self.gemini_keys[self.current_gemini_idx]
            self.current_gemini_idx = (self.current_gemini_idx + 1) % len(self.gemini_keys)
            
            if key_obj.is_available():
                return key_obj.key
            
            if self.current_gemini_idx == start_idx:
                return None # 全部都在冷卻中

    def get_groq_key(self) -> Optional[str]:
        if not self.groq_keys:
            return None
        
        start_idx = self.current_groq_idx
        while True:
            key_obj = self.groq_keys[self.current_groq_idx]
            self.current_groq_idx = (self.current_groq_idx + 1) % len(self.groq_keys)
            
            if key_obj.is_available():
                return key_obj.key
            
            if self.current_groq_idx == start_idx:
                return None

    def report_error(self, key: str, service: str, error_code: int):
        """報錯並觸發冷卻邏輯"""
        keys = self.gemini_keys if service == "gemini" else self.groq_keys
        for k in keys:
            if k.key == key:
                if error_code == 429:
                    k.set_cooldown(60)
                else:
                    k.set_cooldown(30)
                break

    def get_pool_status(self) -> Dict:
        """獲取金鑰池運作狀態"""
        gemini_active = sum(1 for k in self.gemini_keys if k.is_available())
        groq_active = sum(1 for k in self.groq_keys if k.is_available())
        
        return {
            "gemini": {
                "total": len(self.gemini_keys),
                "active": gemini_active,
                "status": "良好" if gemini_active > 0 else "耗盡/冷卻中"
            },
            "groq": {
                "total": len(self.groq_keys),
                "active": groq_active,
                "status": "良好" if groq_active > 0 else "耗盡/冷卻中"
            },
            "limits": {
                "asr_rpm": len(self.groq_keys) * 20,
                "trans_rpm": len(self.gemini_keys) * 15 + len(self.groq_keys) * 30
            }
        }

# 全域單例
key_manager = KeyManager()
