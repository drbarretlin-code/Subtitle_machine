import os
import asyncio
import google.generativeai as genai
from backend.key_manager import key_manager
from typing import Optional

from groq import Groq

class SubtitleEngine:
    def __init__(self):
        self._groq_client: Optional[Groq] = None

    async def _translate_groq(self, prompt: str) -> Optional[str]:
        """利用 Groq LPU 進行極速翻譯"""
        api_key = key_manager.get_groq_key()
        if not api_key:
            return None
            
        try:
            client = Groq(api_key=api_key)
            response = await asyncio.to_thread(
                client.chat.completions.create,
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192", # 極速模型
                temperature=0.2,
                max_tokens=256
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"⚠️ Groq 翻譯失敗: {e}")
            if "429" in str(e):
                key_manager.report_error(api_key, "groq", 429)
            return None

    async def refine_text(self, raw_text: str, context: str = "", target_lang: str = "繁體中文") -> str:
        """混合翻譯引擎：優先 Groq (毫秒級), 備援 Gemini (高品質)"""
        if not raw_text.strip():
            return ""

        prompt = (
            f"You are a professional real-time subtitle translator.\n"
            f"Context: {context}\n"
            f"Raw ASR: {raw_text}\n"
            f"Target: {target_lang}\n\n"
            f"Instructions:\n"
            f"1. Fix ASR errors in 'Raw ASR' using 'Context'.\n"
            f"2. Translate the result into natural {target_lang}.\n"
            f"3. Output ONLY the translation. No preamble, no quotes."
        )

        # 1. 優先嘗試 Groq (追求毫秒級回應)
        print(f"⚡ [Groq] 正在極速轉譯...")
        groq_result = await self._translate_groq(prompt)
        if groq_result:
            print(f"🚀 [Groq] -> {groq_result}")
            return groq_result

        # 2. 若 Groq 失敗，使用 Gemini 備援 (包含自動降級邏輯)
        print(f"🔮 [Gemini] 執行備援轉譯...")
        api_key = key_manager.get_gemini_key()
        if not api_key:
            return raw_text

        try:
            genai.configure(api_key=api_key)
            if not hasattr(self, '_available_models'):
                self._available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                self._last_successful_model = None

            models_to_try = []
            if hasattr(self, '_last_successful_model') and self._last_successful_model:
                models_to_try.append(self._last_successful_model)
            
            sorted_avail = sorted(self._available_models, key=lambda x: ("lite" not in x.lower(), "flash" not in x.lower()))
            for m in sorted_avail:
                if m not in models_to_try:
                    models_to_try.append(m)

            for model_name in models_to_try:
                try:
                    if any(x in model_name for x in ["tts", "robotics", "computer-use"]): continue
                    model = genai.GenerativeModel(model_name)
                    response = await asyncio.to_thread(
                        model.generate_content, 
                        prompt,
                        request_options={"timeout": 6}
                    )
                    refined_text = response.text.strip()
                    self._last_successful_model = model_name
                    print(f"✅ [Gemini-{model_name.replace('models/', '')}] -> {refined_text}")
                    return refined_text
                except:
                    continue
            
            return raw_text
            
        except Exception as e:
            print(f"❌ SubtitleEngine 異常: {e}")
            return raw_text

# 全域單例
subtitle_engine = SubtitleEngine()
