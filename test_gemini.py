import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Make sure your new Gemini API key is loaded
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("❌ GEMINI_API_KEY missing in .env")

# Configure Gemini client with the key
genai.configure(api_key=api_key)

# List available models
try:
    models = genai.list_models()
    print("Available models:")
    for m in models:
        print(m)  # Each model name
except Exception as e:
    print("Error listing models:", e)



