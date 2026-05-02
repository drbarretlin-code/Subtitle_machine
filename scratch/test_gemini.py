import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("GOOGLE_API_KEY")
print(f"Using key: {key[:10]}...")

genai.configure(api_key=key)
model = genai.GenerativeModel('gemini-1.5-flash')

try:
    response = model.generate_content("Hello, this is a test.")
    print("Response:", response.text)
except Exception as e:
    print("Error:", e)
