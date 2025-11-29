import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import webbrowser
import requests
import datetime
import random
from offline_listener import handle_offline_command
import google.generativeai as genai

# === Load environment variables ===
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

app = Flask(__name__)

# === Configure Gemini ===
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
try:
    model = genai.GenerativeModel("models/gemini-2.5-flash")
    print("✅ Gemini 2.5 Flash model initialized successfully.")
except Exception as e:
    model = None
    print(f"⚠️ Gemini model not available: {e}")


# === Weather Function ===
def get_weather(city):
    if not WEATHER_API_KEY:
        return "⚠️ Weather API not configured."

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            return f"⚠️ City '{city}' not found."

        temp = data["main"]["temp"]
        condition = data["weather"][0]["description"]
        return f"🌤️ Weather in {city.title()}: {temp}°C, {condition}"
    except Exception as e:
        return f"⚠️ Error fetching weather: {e}"


# === Local Command Handler (Offline Mode) ===
def handle_local_command(command):
    command = command.lower().strip()

    # Time
    if "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return True, f"🕒 The current time is {now}"

    # Date
    if "date" in command:
        today = datetime.date.today().strftime("%B %d, %Y")
        return True, f"📅 Today's date is {today}"

    # Notepad
    if "open notepad" in command:
        os.system("notepad")
        return True, "📝 Opening Notepad"

    # Browser
    if "open browser" in command or "google" in command:
        webbrowser.open("https://www.google.com") 
        return True, "🌐 Opening Google"

    # YouTube
    if "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        return True, "🌐 Opening YouTube"

    # Music
    if "play music" in command:
        music_folder = r"C:\FAMILY\Shravani\music"  # ⬅️ Update path
        try:
            songs = os.listdir(music_folder)
            if songs:
                song = random.choice(songs)
                os.startfile(os.path.join(music_folder, song))
                return True, f"🎵 Playing {song}"
            else:
                return True, "⚠️ No songs found in your music folder."
        except Exception as e:
            return True, f"⚠️ Could not play music: {e}"

    return False, ""


# === Routes ===
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message", "")
    if not user_message:
        return jsonify({"reply": "⚠️ No input received."})

    print("User said:", user_message)
    txt = user_message.lower().strip()

    # 1️⃣ Handle local commands first (offline support)
    handled, reply = handle_local_command(txt)
    if handled:
        return jsonify({"reply": reply})

    # 2️⃣ If still matches offline pattern, pass to offline listener
    offline_keywords = ["time", "date", "notepad", "music", "browser", "youtube", "stop", "exit"]
    if any(word in txt for word in offline_keywords):
        reply = handle_offline_command(txt)
        return jsonify({"reply": reply})

    # 3️⃣ Weather
    if "weather" in txt:
        words = txt.split()
        city = words[-1] if len(words) > 1 else "Mumbai"
        reply = get_weather(city)
        return jsonify({"reply": reply})

    # 4️⃣ Gemini AI fallback
    try:
        prompt = "Answer briefly in 2 lines: " + user_message
        response = model.generate_content(prompt)
        ai_reply = response.text if hasattr(response, "text") else "⚠️ No response from Gemini."
    except Exception as e:
        ai_reply = f"⚠️ Gemini API not available (Error: {e})"

    return jsonify({"reply": ai_reply})


# === Run Flask App ===
if __name__ == "__main__":
    app.run(debug=True)
