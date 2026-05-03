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

        try:
            genai.configure(api_key=api_key)
            
            # 1. 動態獲取清單
            if not hasattr(self, '_available_models'):
                print("🔍 正在檢索可用模型...")
                self._available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
                # 優先權排序：已成功的 > Lite > Flash > 其他
                self._last_successful_model = None

            # 2. 構建嘗試清單
            # 優先嘗試上次成功的
            models_to_try = []
            if hasattr(self, '_last_successful_model') and self._last_successful_model:
                models_to_try.append(self._last_successful_model)
            
            # 排序：lite > flash > 其他 (lite 通常限制較寬且速度快)
            sorted_avail = sorted(self._available_models, key=lambda x: ("lite" not in x.lower(), "flash" not in x.lower()))
            for m in sorted_avail:
                if m not in models_to_try:
                    models_to_try.append(m)

            refined_text = None
            used_model = None
            
            for model_name in models_to_try:
                try:
                    # 避免嘗試已知不支援 TEXT 的特殊模型
                    if any(x in model_name for x in ["tts", "robotics", "computer-use"]): continue
                    
                    print(f"🔮 嘗試: {model_name.replace('models/', '')}...")
                    model = genai.GenerativeModel(model_name)
                    response = await asyncio.to_thread(
                        model.generate_content, 
                        prompt,
                        request_options={"timeout": 6} # 縮短超時
                    )
                    refined_text = response.text.strip()
                    used_model = model_name
                    self._last_successful_model = model_name # 紀錄成功模型
                    break
                except Exception as model_err:
                    err_str = str(model_err)
                    print(f"⚠️ {model_name.replace('models/', '')} 失敗: {err_str[:50]}")
                    # 若是 Quota 問題，直接嘗試下一個
                    continue
            
            if not refined_text:
                return raw_text

            print(f"✅ [{used_model.replace('models/', '')}] -> {refined_text}")
            return refined_text
            
        except Exception as e:
            print(f"❌ SubtitleEngine 異常: {e}")
            return raw_text

# 全域單例
subtitle_engine = SubtitleEngine()
