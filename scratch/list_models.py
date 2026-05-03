import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GOOGLE_API_KEYS") or os.getenv("GOOGLE_API_KEY")
if not key:
    print("❌ No key found in .env")
else:
    print(f"🔑 Using key: {key[:8]}...")
    genai.configure(api_key=key)
    try:
        print("🔍 Listing available models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"- {m.name} (Display: {m.display_name})")
    except Exception as e:
        print(f"❌ Error listing models: {e}")
