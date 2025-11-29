from dotenv import load_dotenv
import os

load_dotenv()
print("Gemini API Key:", os.getenv("GEMINI_API_KEY"))
print("Weather API Key:", os.getenv("WEATHER_API_KEY"))

