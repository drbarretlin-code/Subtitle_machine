import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=key)

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
except Exception as e:
    print("Error:", e)
