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
            
            # 動態獲取可用模型清單 (快取機制)
            if not hasattr(self, '_available_models'):
                print("🔍 正在動態檢索可用模型清單...")
                self._available_models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        # 排除一些特殊用途模型 (如 robotics, computer-use)
                        if any(x in m.name for x in ["robotics", "computer-use", "clip"]):
                            continue
                        self._available_models.append(m.name)
                print(f"✅ 發現 {len(self._available_models)} 個可用模型: {self._available_models[:3]}...")

            refined_text = None
            used_model = None
            
            # 優先嘗試 Flash 或 Pro 字樣的模型
            models_to_try = sorted(self._available_models, key=lambda x: ("flash" not in x, "pro" not in x))
            
            for model_name in models_to_try:
                try:
                    print(f"🔮 嘗試模型: {model_name} (Target: {target_lang})...")
                    model = genai.GenerativeModel(model_name)
                    response = await asyncio.to_thread(
                        model.generate_content, 
                        prompt,
                        request_options={"timeout": 10}
                    )
                    refined_text = response.text.strip()
                    used_model = model_name
                    break
                except Exception as model_err:
                    print(f"⚠️ 模型 {model_name} 失敗: {str(model_err)[:80]}")
                    continue
            
            if not refined_text:
                print("❌ 遍歷所有可用模型均失敗，請確認金鑰配額。")
                return raw_text

            print(f"✨ {used_model} 成功轉譯: [{refined_text}]")
            return refined_text
            
        except Exception as e:
            print(f"❌ SubtitleEngine 核心異常: {e}")
            return raw_text

# 全域單例
subtitle_engine = SubtitleEngine()
