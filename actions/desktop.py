# ============================================
# NOVA - Desktop Control (desktop.py)
# ============================================

import subprocess
import os
import sys
import webbrowser
import pyautogui
import time
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

class DesktopController:
    def __init__(self):
        pyautogui.FAILSAFE = True
        
        # ---- App shortcuts ----
        self.apps = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
            "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
            "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "explorer": "explorer.exe",
            "task manager": "taskmgr.exe",
            "control panel": "control.exe",
            "spotify": r"C:\Users\Work\AppData\Roaming\Spotify\Spotify.exe",
            "vlc": r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            "vs code": r"C:\Users\Work\AppData\Local\Programs\Microsoft VS Code\Code.exe",
            "vscode": r"C:\Users\Work\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        }
        
        # ---- Website shortcuts ----
        self.websites = {
            "youtube": "https://www.youtube.com",
            "google": "https://www.google.com",
            "github": "https://www.github.com",
            "gmail": "https://mail.google.com",
            "netflix": "https://www.netflix.com",
            "facebook": "https://www.facebook.com",
            "instagram": "https://www.instagram.com",
            "twitter": "https://www.twitter.com",
            "whatsapp": "https://web.whatsapp.com",
            "chatgpt": "https://chat.openai.com",
            "reddit": "https://www.reddit.com",
            "linkedin": "https://www.linkedin.com",
        }
        
        print("✅ Desktop controller ready!")

    # ============================================
    # OPEN APP
    # ============================================
    def open_app(self, app_name):
        app_name = app_name.lower().strip()
        
        if app_name in self.apps:
            app_path = self.apps[app_name]
            try:
                subprocess.Popen(app_path)
                return f"Opening {app_name}!"
            except FileNotFoundError:
                try:
                    subprocess.Popen(app_path, shell=True)
                    return f"Opening {app_name}!"
                except:
                    return f"Could not find {app_name}. Is it installed?"
        else:
            try:
                subprocess.Popen(app_name, shell=True)
                return f"Trying to open {app_name}!"
            except:
                return f"I don't know how to open {app_name} yet."

    # ============================================
    # OPEN WEBSITE
    # ============================================
    def open_website(self, site_name):
        site_name = site_name.lower().strip()
        
        if site_name in self.websites:
            webbrowser.open(self.websites[site_name])
            return f"Opening {site_name}!"
        elif "." in site_name:
            if not site_name.startswith("http"):
                site_name = "https://" + site_name
            webbrowser.open(site_name)
            return f"Opening {site_name}!"
        else:
            return f"I don't know the website for {site_name}."

    # ============================================
    # SEARCH GOOGLE
    # ============================================
    def search_google(self, query):
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching Google for: {query}"

    # ============================================
    # SEARCH YOUTUBE
    # ============================================
    def search_youtube(self, query):
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching YouTube for: {query}"

    # ============================================
    # OPEN CAMERA
    # ============================================
    def open_camera(self):
        try:
            subprocess.Popen("start microsoft.windows.camera:", shell=True)
            return "Opening camera!"
        except:
            return "Could not open camera."

    # ============================================
    # TAKE SCREENSHOT
    # ============================================
    def take_screenshot(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/screenshot_{timestamp}.png"
            os.makedirs("data", exist_ok=True)
            screenshot = pyautogui.screenshot()
            screenshot.save(filename)
            
            # Open screenshot immediately!
            os.startfile(os.path.abspath(filename))
            
            return f"Screenshot saved and opened!"
        except Exception as e:
            return f"Could not take screenshot: {e}"

    # ============================================
    # VOLUME CONTROL
    # ============================================
    def volume_up(self):
        for _ in range(5):
            pyautogui.press('volumeup')
        return "Volume up!"

    def volume_down(self):
        for _ in range(5):
            pyautogui.press('volumedown')
        return "Volume down!"

    def mute(self):
        pyautogui.press('volumemute')
        return "Muted!"

    # ============================================
    # SYSTEM CONTROLS
    # ============================================
    def shutdown(self):
        subprocess.run(["shutdown", "/s", "/t", "30"])
        return "Shutting down in 30 seconds! Say cancel shutdown to stop."

    def cancel_shutdown(self):
        subprocess.run(["shutdown", "/a"])
        return "Shutdown cancelled!"

    def restart(self):
        subprocess.run(["shutdown", "/r", "/t", "30"])
        return "Restarting in 30 seconds!"

    def lock_screen(self):
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
        return "Screen locked!"

    # ============================================
    # TYPE TEXT
    # ============================================
    def type_text(self, text):
        pyautogui.typewrite(text, interval=0.05)
        return f"Typed: {text}"

    # ============================================
    # GET TIME AND DATE
    # ============================================
    def get_time(self):
        now = datetime.now()
        return f"It is {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d %Y')}"

    # ============================================
    # PROCESS VOICE COMMAND
    # ============================================
    def process_command(self, command):
        command_lower = command.lower().strip()
        
        # ---- Open commands ----
        if "open" in command_lower:
            if "camera" in command_lower:
                return self.open_camera()
            
            for site in self.websites:
                if site in command_lower:
                    return self.open_website(site)
            
            for app in self.apps:
                if app in command_lower:
                    return self.open_app(app)

        # ---- Search commands ----
        if "search" in command_lower or "look up" in command_lower:
            if "youtube" in command_lower:
                query = command_lower.replace("search youtube for", "").replace("search youtube", "").replace("on youtube", "").strip()
                return self.search_youtube(query)
            else:
                query = command_lower.replace("search google for", "").replace("search for", "").replace("search", "").replace("look up", "").strip()
                return self.search_google(query)

        # ---- Screenshot ----
        if "screenshot" in command_lower or "take a photo of screen" in command_lower:
            return self.take_screenshot()

        # ---- Volume ----
        if "volume up" in command_lower or "turn up" in command_lower:
            return self.volume_up()
        if "volume down" in command_lower or "turn down" in command_lower:
            return self.volume_down()
        if "mute" in command_lower:
            return self.mute()

        # ---- Time ----
        if "what time" in command_lower or "what's the time" in command_lower:
            return self.get_time()

        # ---- System ----
        if "lock" in command_lower and "screen" in command_lower:
            return self.lock_screen()
        if "shutdown" in command_lower and "cancel" not in command_lower:
            return self.shutdown()
        if "cancel shutdown" in command_lower:
            return self.cancel_shutdown()
        if "restart" in command_lower:
            return self.restart()

        # ---- Not a desktop command ----
        return None


# ============================================
# TEST
# ============================================
if __name__ == "__main__":
    print("🔱 Testing Desktop Controller...")
    desktop = DesktopController()
    
    tests = [
        "what time is it",
        "open notepad",
        "open youtube",
        "search google for Nepali MMA fighters",
        "take a screenshot",
    ]
    
    for test in tests:
        print(f"\n🎙️ Command: {test}")
        result = desktop.process_command(test)
        print(f"✅ Result: {result}")
        time.sleep(2)