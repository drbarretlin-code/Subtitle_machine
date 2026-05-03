import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GOOGLE_API_KEY")
if key:
    print(f"Loaded key: {key[:5]}...{key[-5:]}")
else:
    print("No GOOGLE_API_KEY found!")
