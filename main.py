import os
import google.generativeai as genai
import speech_recognition as sr
import pyttsx3
import webbrowser
from datetime import datetime
from dotenv import load_dotenv

# ------------------------------
# 1. Load API Key
# ------------------------------
# Try loading from .env
load_dotenv(dotenv_path=".env")
api_key = os.getenv("AIzaSyCapeVh5JCByVfxjoVBpG1F36bmCyxHeGQ")

# If not found, fallback to hardcoded key
if not api_key or api_key.strip() == "":
    # 🚨 Replace this with your real API key
    api_key = "AIzaSyCapeVh5JCByVfxjoVBpG1F36bmCyxHeGQ"

if not api_key or api_key.strip() == "":
    raise ValueError("❌ API Key missing. Please set in .env or inside the code.")

# Configure Gemini
genai.configure(api_key=api_key)

# ------------------------------
# 2. Text-to-Speech setup
# ------------------------------
engine = pyttsx3.init()
engine.setProperty('rate', 170)
engine.setProperty('volume', 1)

def speak(text):
    print(f"\n🤖 Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

# ------------------------------
# 3. Speech-to-Text setup
# ------------------------------
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n🎤 Listening...")
        r.pause_threshold = 1
        audio = r.listen(source, phrase_time_limit=8)
    try:
        print("📝 Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        print(f"🗣️ You: {query}")
        return query.lower()
    except sr.UnknownValueError:
        speak("Sorry, I could not understand. Please repeat.")
        return ""
    except sr.RequestError:
        speak("Network error. Please check your internet connection.")
        return ""

# ------------------------------
# 4. Ask Gemini API
# ------------------------------
def ask_gemini(prompt):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error: {e}"

# ------------------------------
# 5. Custom Commands
# ------------------------------
def handle_custom_commands(query):
    if "open youtube" in query:
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube.")
        return True
    elif "open google" in query:
        webbrowser.open("https://google.com")
        speak("Opening Google.")
        return True
    elif "time" in query:
        current_time = datetime.now().strftime("%I:%M %p")
        speak(f"The time is {current_time}.")
        return True
    elif "date" in query:
        today_date = datetime.now().strftime("%B %d, %Y")
        speak(f"Today's date is {today_date}.")
        return True
    return False

# ------------------------------
# 6. Main loop
# ------------------------------
def main():
    speak("Hello there! How can I help you today?")
    while True:
        query = listen()

        if query in ["exit", "quit", "stop"]:
            speak("Goodbye!")
            break

        if handle_custom_commands(query):
            continue

        # Ask Gemini API
        answer = ask_gemini(query)
        speak(answer)

# ------------------------------
# Run Assistant
# ------------------------------
if __name__ == "__main__":
    main()
