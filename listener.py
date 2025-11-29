import speech_recognition as sr
import webbrowser
import subprocess
import time
import requests
import sys
import os
from pathlib import Path

# CONFIG 
# Add the wake words you want to recognize (lowercase)
WAKE_WORDS = ["hey alexa", "alexa"]

# URL your Flask app serves on
FLASK_URL = "http://127.0.0.1:5000/"

# Path to app.py (assumes it's in the same folder as this listener)
BASE_DIR = Path(__file__).resolve().parent
APP_PY = BASE_DIR / "app.py"

# Which Python to use to start app.py: use same interpreter running listener.py
PYTHON_EXEC = sys.executable

# Should we stop listening after opening the UI once? Set False to keep listening.
STOP_AFTER_OPEN = False

# How long to wait (seconds) for Flask to start
FLASK_START_TIMEOUT = 30

# helpers 
def is_flask_running(url=FLASK_URL, timeout=1):
    try:
        r = requests.get(url, timeout=timeout)
        return r.status_code == 200
    except Exception:
        return False

def start_flask():
    """Start app.py with same python interpreter. Returns subprocess.Popen or None."""
    if not APP_PY.exists():
        print(f"❌ app.py not found at: {APP_PY}")
        return None
    try:
        print(f"🚀 Starting Flask app with: {PYTHON_EXEC} {APP_PY}")
        # start the process in background; keep stdout/stderr visible for debugging
        proc = subprocess.Popen([PYTHON_EXEC, str(APP_PY)], cwd=str(BASE_DIR))
        return proc
    except Exception as e:
        print("⚠️ Failed to start Flask:", e)
        return None

def open_browser(url=FLASK_URL):
    try:
        print("🌐 Attempting to open browser at", url)
        opened = webbrowser.open(url, new=2)  # new tab if possible
        if opened:
            print("✅ webbrowser.open reported success.")
            return True
    except Exception as e:
        print("⚠️ webbrowser.open failed:", e)

    # Platform-specific fallbacks
    try:
        if os.name == "nt":  # Windows
            os.startfile(url)
            print("✅ opened via os.startfile")
            return True
        elif sys.platform == "darwin":  # macOS
            subprocess.Popen(["open", url])
            print("✅ opened via open (macOS)")
            return True
        else:  # Linux / xdg-open
            subprocess.Popen(["xdg-open", url])
            print("✅ opened via xdg-open (Linux)")
            return True
    except Exception as e:
        print("⚠️ fallback browser open failed:", e)
    return False

# main listener loop
def listen_for_wake_word():
    recognizer = sr.Recognizer()

    # Choose microphone: default. If you have multiple mics, change index.
    try:
        mic = sr.Microphone()
    except Exception as e:
        print("❌ Could not access microphone:", e)
        return

    print(f"🎤 Listening for wake words: {WAKE_WORDS} ... (press Ctrl+C to stop)")

    flask_proc = None
    already_opened = False

    while True:
        with mic as source:
            try:
                recognizer.adjust_for_ambient_noise(source, duration=0.6)
            except Exception:
                # sometimes this fails on some systems; ignore
                pass

            print("Listening...")
            try:
                audio = recognizer.listen(source, timeout=6, phrase_time_limit=5)
            except sr.WaitTimeoutError:
                print("⏳ Listen timeout, retrying...")
                continue

        try:
            # using Google recognizer — requires internet
            command = recognizer.recognize_google(audio).lower().strip()
            print("Heard:", command)
        except sr.UnknownValueError:
            # nothing recognized
            # print("...no speech recognized")
            continue
        except sr.RequestError as e:
            # network/recognizer error (e.g., getaddrinfo failed)
            print("⚠️ Recognition request error:", e)
            # If offline recognition needed, consider pocketsphinx or Porcupine
            time.sleep(2)
            continue
        except Exception as e:
            print("⚠️ Recognition unexpected error:", e)
            time.sleep(1)
            continue

        # Check if any wake word substring appears in the recognized text
        for wake in WAKE_WORDS:
            if wake in command:
                print(f"✅ Wake word detected: '{wake}'")

                # Start Flask if not running
                if not is_flask_running():
                    print("Flask not running; starting it now...")
                    flask_proc = start_flask()

                    # Wait for Flask to become responsive
                    waited = 0
                    while waited < FLASK_START_TIMEOUT:
                        if is_flask_running():
                            print(f"✅ Flask responded at {FLASK_URL}")
                            print("🕐 Giving Flask a few more seconds to fully load UI...")
                            time.sleep(3)  # <-- small delay before opening browser
                            break
                        time.sleep(1)
                        waited += 1
                        print(f"Waiting for Flask... {waited}s")
                    else:
                        print(f"❌ Flask did not start within {FLASK_START_TIMEOUT} seconds.")
                        # even if Flask failed, try to open browser anyway
                else:
                    print("Flask already running.")

                # Open the assistant UI in browser (with fallback methods)
                success = open_browser()
                if not success:
                    print("❌ Failed to open browser automatically. Please open:", FLASK_URL)
                else:
                    already_opened = True

                # Stop or continue listening based on config
                if STOP_AFTER_OPEN:
                    print("Listener stopping after opening UI.")
                    return
                else:
                    print("Continuing to listen for wake word...")
                    # small cooldown to avoid duplicate triggers
                    time.sleep(2)
                break  # break inner for-loop, continue outer while loop

            print("✨ Assistant is ready! You can now talk or type in the web UI.")


# Entry point
if __name__ == "__main__":
    try:
        listen_for_wake_word()
    except KeyboardInterrupt:
        print("\n🛑 Listener stopped by user.")

