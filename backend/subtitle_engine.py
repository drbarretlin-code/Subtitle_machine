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
            'gemini-1.5-pro',
            'gemini-2.0-flash-exp',
            'gemini-pro',
            'gemini-3-flash', # 預留未來版本
            'gemini-1.0-pro'
        ]

        try:
            genai.configure(api_key=api_key)
            
            refined_text = None
            used_model = None
            
            for model_name in models_to_try:
                try:
                    print(f"🔮 嘗試模型: {model_name} (Target: {target_lang})...")
                    model = genai.GenerativeModel(model_name)
                    response = await asyncio.to_thread(
                        model.generate_content, 
                        prompt,
                        # 設定較短的超時
                        request_options={"timeout": 5}
                    )
                    refined_text = response.text.strip()
                    used_model = model_name
                    break # 成功則跳出循環
                except Exception as model_err:
                    print(f"⚠️ 模型 {model_name} 失敗: {str(model_err)[:100]}")
                    continue
            
            if not refined_text:
                print("❌ 所有 Gemini 模型均無法產生內容，請檢查金鑰權限或網路狀態")
                return raw_text

            print(f"✨ {used_model} 回傳: [{refined_text}]")
            
            # 安全檢查
            forbidden = ["ASR", "Text:", "Task:", "翻譯", "字幕"]
            if any(kw in refined_text for kw in forbidden):
                print("⚠️ 偵測到無效翻譯內容")
                return raw_text
                
            return refined_text
            
        except Exception as e:
            print(f"❌ SubtitleEngine 核心錯誤: {e}")
            return raw_text

# 全域單例
subtitle_engine = SubtitleEngine()
