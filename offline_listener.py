import os
import sys
import webbrowser
import datetime
import requests

# Flask backend chat route (local fallback)
FLASK_CHAT_URL = "http://127.0.0.1:5000/chat"


def send_to_flask(command):
    """
    Sends unrecognized commands to Flask backend (AI model or online mode)
    """
    try:
        response = requests.post(FLASK_CHAT_URL, json={"message": command})
        if response.status_code == 200:
            return response.json().get("reply", "No response from AI backend.")
        else:
            return f"⚠️ Flask returned error {response.status_code}"
    except Exception as e:
        return f"⚠️ Failed to connect to Flask backend: {e}"


def handle_offline_command(command):
    """
    Handles basic offline system commands.
    """
    command = command.lower().strip()

    # --- Time ---
    if "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"🕒 Current time is {now}"

    # --- Date ---
    elif "date" in command:
        today = datetime.date.today().strftime("%B %d, %Y")
        return f"📅 Today's date is {today}"

    # --- Open YouTube ---
    elif "open youtube" in command:
        webbrowser.open("https://www.youtube.com")
        return "🌐 Opening YouTube"

    # --- Open Browser / Google ---
    elif "open browser" in command or "google" in command:
        webbrowser.open("https://www.google.com")
        return "🌐 Opening Browser"

    # --- Open Notepad ---
    elif "open notepad" in command:
        os.system("notepad")
        return "📝 Opening Notepad"

    # --- Play Music ---
    elif "music" in command:
        music_folder = r"C:\Users\YourName\Music"  # ⬅️ Update this path
        try:
            os.startfile(music_folder)
            return "🎵 Opening Music Folder"
        except Exception as e:
            return f"⚠️ Could not open music folder: {e}"

    # --- Stop / Exit ---
    elif "stop" in command or "exit" in command:
        print("👋 Stopping offline assistant.")
        sys.exit(0)

    # --- Unrecognized (Send to Flask) ---
    else:
        return send_to_flask(command)
