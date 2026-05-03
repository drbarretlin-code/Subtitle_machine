import os
import asyncio
import google.generativeai as genai
from backend.key_manager import key_manager
from typing import Optional

class SubtitleEngine:
    def __init__(self):
        pass

    async def refine_text(self, raw_text: str, context: str = "", target_lang: str = "繁體中文") -> str:
        """利用 Gemini 金鑰池進行翻譯與校正"""
        if not raw_text.strip():
            return ""

        api_key = key_manager.get_gemini_key()
        if not api_key:
            return raw_text # 無金鑰時回傳原始文字

        prompt = (
            f"You are a professional real-time subtitle translator.\n"
            f"Context: {context}\n"
            f"Raw ASR: {raw_text}\n"
            f"Target: {target_lang}\n\n"
            f"Instructions:\n"
            f"1. Fix ASR errors in 'Raw ASR' using 'Context'.\n"
            f"2. Translate the result into natural {target_lang}.\n"
            f"3. Output ONLY the translation. No preamble, no quotes.\n"
            f"4. If 'Raw ASR' is noise or background sound, return an empty string."
        )

        models_to_try = [
            'gemini-1.5-flash',
            'gemini-1.5-flash-latest',
            'gemini-pro',
            'gemini-1.0-pro'
        ]

        try:
            genai.configure(api_key=api_key)
            
            # 尋找可用的模型
            model = None
            for model_name in models_to_try:
                try:
                    temp_model = genai.GenerativeModel(model_name)
                    # 測試性呼叫或直接指派
                    model = temp_model
                    break
                except:
                    continue
            
            if not model:
                print("❌ 所有 Gemini 模型均無法初始化")
                return raw_text

            print(f"🔮 發送翻譯請求 (模型: {model_name}, Target: {target_lang})...")
            response = await asyncio.to_thread(
                model.generate_content, 
                prompt
            )
            
            refined_text = response.text.strip()
            print(f"✨ Gemini 回傳: [{refined_text}]")
            
            # 安全檢查：避免 AI 回傳提示詞
            forbidden = ["ASR", "Text:", "Task:", "翻譯", "字幕"]
            if any(kw in refined_text for kw in forbidden):
                print("⚠️ 偵測到無效翻譯內容，回退至原始文字")
                return raw_text
                
            return refined_text
        except Exception as e:
            print(f"❌ Gemini 翻譯失敗 (Key: {api_key[:8]}...): {e}")
            if "429" in str(e):
                key_manager.report_error(api_key, "gemini", 429)
            return raw_text

# 全域單例
subtitle_engine = SubtitleEngine()
