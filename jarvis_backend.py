"""
JARVIS Backend - AI Assistant Core Engine
Handles all voice recognition, speech synthesis, app control, web operations, and AI responses
"""

import os
import sys
import webbrowser
import subprocess
import platform
import datetime
import requests
import json
import threading
import time
import queue
from typing import Optional, Dict, Any
import google.generativeai as genai
import pywhatkit as kit
import pyautogui
import wikipediaapi

# For speech recognition and synthesis
try:
    import pyttsx3
    import speech_recognition as sr
except ImportError:
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyttsx3", "SpeechRecognition", "pyaudio"])
    import pyttsx3
    import speech_recognition as sr


class JarvisBackend:
    """Main backend class for JARVIS AI Assistant"""
    
    def __init__(self, api_key: str, weather_api_key: str = "bd5e378503939ddaee76f12ad7a97608"):
        """Initialize JARVIS with Gemini API key"""
        self.api_key = api_key
        self.weather_api_key = weather_api_key
        self.setup_gemini()
        self.setup_speech_engine()
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        self.system_platform = platform.system()
        
        # Speech queue and lock for thread-safe speech
        self.speech_queue = queue.Queue()
        self.speech_lock = threading.Lock()
        self.speech_thread_running = False
        self.start_speech_worker()
        
        # Common applications database
        self.apps = self.get_system_apps()
        
        # WhatsApp contacts database
        self.contacts = {
            "soumya jain": "+919772712490",
            "soumya": "+919772712490",
            "aditya": "+919588072722",
            "manan jain": "+918824343285",
            "manan": "+918824343285",
            "deepak": "+917877179204",
        }
        
    def setup_gemini(self):
        """Configure Gemini AI"""
        try:
            genai.configure(api_key=self.api_key)
            # Use the latest Gemini 2.5 Flash model
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.chat = self.model.start_chat(history=[])
            print("✓ Gemini AI initialized successfully")
        except Exception as e:
            print(f"✗ Error initializing Gemini: {e}")
            self.model = None
            
    def setup_speech_engine(self):
        """Initialize text-to-speech engine"""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 180)  # Speed
            self.engine.setProperty('volume', 0.9)  # Volume
            
            # Set voice (try to get a good one)
            voices = self.engine.getProperty('voices')
            if len(voices) > 1:
                self.engine.setProperty('voice', voices[1].id)  # Usually female voice
            print("✓ Text-to-speech initialized")
        except Exception as e:
            print(f"✗ Error initializing TTS: {e}")
            self.engine = None
    
    def start_speech_worker(self):
        """Start background thread for speech processing"""
        def speech_worker():
            self.speech_thread_running = True
            while self.speech_thread_running:
                try:
                    # Get text from queue with timeout
                    text = self.speech_queue.get(timeout=0.5)
                    
                    if text and self.engine:
                        with self.speech_lock:
                            try:
                                # Stop any ongoing speech
                                try:
                                    self.engine.stop()
                                except:
                                    pass
                                
                                # Speak the text
                                self.engine.say(text)
                                self.engine.runAndWait()
                            except Exception as e:
                                print(f"Speech error: {e}")
                    
                    self.speech_queue.task_done()
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Speech worker error: {e}")
        
        thread = threading.Thread(target=speech_worker, daemon=True)
        thread.start()
    
    def get_system_apps(self) -> Dict[str, str]:
        """Get common applications based on OS"""
        if self.system_platform == "Windows":
            return {
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "paint": "mspaint.exe",
                "chrome": "chrome.exe",
                "google chrome": "chrome.exe",
                "firefox": "firefox.exe",
                "edge": "msedge.exe",
                "microsoft edge": "msedge.exe",
                "explorer": "explorer.exe",
                "file explorer": "explorer.exe",
                "cmd": "cmd.exe",
                "command prompt": "cmd.exe",
                "powershell": "powershell.exe",
                "task manager": "taskmgr.exe",
                "control panel": "control.exe",
                "settings": "ms-settings:",
                "word": "winword.exe",
                "excel": "excel.exe",
                "powerpoint": "powerpnt.exe",
                "outlook": "outlook.exe",
                "vscode": "code.exe",
                "visual studio code": "code.exe",
                "spotify": "spotify.exe",
                "discord": "discord.exe",
                "steam": "steam.exe",
            }
        elif self.system_platform == "Darwin":  # macOS
            return {
                "safari": "Safari",
                "chrome": "Google Chrome",
                "firefox": "Firefox",
                "notes": "Notes",
                "calculator": "Calculator",
                "terminal": "Terminal",
                "finder": "Finder",
                "spotify": "Spotify",
            }
        else:  # Linux
            return {
                "firefox": "firefox",
                "chrome": "google-chrome",
                "terminal": "gnome-terminal",
                "calculator": "gnome-calculator",
                "files": "nautilus",
                "text editor": "gedit",
            }
    
    def speak(self, text: str):
        """Convert text to speech using queue for thread safety"""
        print(f"JARVIS: {text}")
        if self.engine:
            # Add to queue instead of direct call
            self.speech_queue.put(text)
        return text
    
    def listen(self) -> Optional[str]:
        """Listen to microphone and convert speech to text"""
        try:
            with sr.Microphone() as source:
                print("🎤 Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
            print("🔄 Recognizing...")
            text = self.recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text.lower()
            
        except sr.WaitTimeoutError:
            # Timeout - no speech detected, don't speak error
            return None
        except sr.UnknownValueError:
            # Could not understand audio - don't spam with error messages
            return None
        except Exception as e:
            print(f"Error in speech recognition: {e}")
            return None
    
    def open_application(self, app_name: str) -> str:
        """Open an application"""
        app_name = app_name.lower().strip()
        
        # Check if app is in our database
        for key, app_path in self.apps.items():
            if key in app_name or app_name in key:
                try:
                    if self.system_platform == "Windows":
                        if app_path.startswith("ms-"):
                            os.system(f'start {app_path}')
                        else:
                            # Use start command for better compatibility
                            os.system(f'start "" {app_path}')
                    elif self.system_platform == "Darwin":
                        subprocess.Popen(["open", "-a", app_path])
                    else:
                        subprocess.Popen(app_path, shell=True)
                    
                    return f"Opening {key}"
                except Exception as e:
                    return f"Error opening {key}: {str(e)}"
        
        return f"I don't know how to open {app_name}. Try: {', '.join(list(self.apps.keys())[:8])}"
    
    def close_application(self, app_name: str) -> str:
        """Close an application"""
        app_name = app_name.lower()
        
        try:
            if self.system_platform == "Windows":
                # Find matching process
                for key in self.apps.keys():
                    if key in app_name or app_name in key:
                        process_name = self.apps[key]
                        os.system(f'taskkill /F /IM {process_name}')
                        return f"Closing {key}"
                        
            elif self.system_platform == "Darwin":
                for key, app_path in self.apps.items():
                    if key in app_name or app_name in key:
                        os.system(f'pkill -f "{app_path}"')
                        return f"Closing {key}"
            else:
                for key, app_path in self.apps.items():
                    if key in app_name or app_name in key:
                        os.system(f'pkill -f {app_path}')
                        return f"Closing {key}"
                        
            return f"Couldn't find {app_name} to close"
            
        except Exception as e:
            return f"Error closing application: {str(e)}"
    
    def search_web(self, query: str) -> str:
        """Search the web using default browser"""
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            return f"Searching for {query}"
        except Exception as e:
            return f"Error searching web: {str(e)}"
    
    def get_weather(self, city: str = "auto") -> str:
        """Get weather information using OpenWeatherMap API"""
        try:
            # Use OpenWeatherMap API
            if city == "auto" or city == "":
                # Get weather for user's location (using IP-based location)
                # First get location from IP
                try:
                    ip_response = requests.get('http://ip-api.com/json/', timeout=3)
                    if ip_response.status_code == 200:
                        location_data = ip_response.json()
                        city = location_data.get('city', 'London')
                except:
                    city = "London"  # Fallback
            
            # Get weather data from OpenWeatherMap
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_api_key}&units=metric"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract weather information
                city_name = data['name']
                country = data['sys']['country']
                temp_c = data['main']['temp']
                temp_f = (temp_c * 9/5) + 32
                feels_like_c = data['main']['feels_like']
                condition = data['weather'][0]['description'].capitalize()
                humidity = data['main']['humidity']
                wind_speed = data['wind']['speed']
                
                weather_info = (
                    f"Weather in {city_name}, {country}: "
                    f"{condition}, {temp_c:.1f}°C ({temp_f:.1f}°F), "
                    f"Feels like {feels_like_c:.1f}°C, "
                    f"Humidity: {humidity}%, "
                    f"Wind: {wind_speed} m/s"
                )
                return weather_info
            elif response.status_code == 404:
                return f"City '{city}' not found. Please check the spelling."
            else:
                return f"Unable to fetch weather information. Error: {response.status_code}"
                
        except Exception as e:
            return f"Error getting weather: {str(e)}"
    
    def get_time(self) -> str:
        """Get current time"""
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M %p")
        return f"The current time is {time_str}"
    
    def get_date(self) -> str:
        """Get current date"""
        now = datetime.datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        return f"Today is {date_str}"
    
    def send_whatsapp_message(self, contact_name: str, message: str) -> str:
        """Send WhatsApp message to a contact"""
        try:
            # Normalize contact name
            contact_name = contact_name.lower().strip()
            
            # Check if contact exists
            if contact_name in self.contacts:
                phone_number = self.contacts[contact_name]
                
                # Get current time and add 2 minutes for scheduling
                now = datetime.datetime.now()
                hour = now.hour
                minute = now.minute + 2
                
                # Adjust if minute exceeds 59
                if minute >= 60:
                    minute -= 60
                    hour += 1
                
                # Send message using pywhatkit
                print(f"Sending WhatsApp message to {contact_name} ({phone_number})...")
                kit.sendwhatmsg(phone_number, message, hour, minute)
                
                return f"WhatsApp message scheduled to {contact_name}. WhatsApp Web will open in 2 minutes."
            else:
                # Contact not found, ask for number
                return f"Contact '{contact_name}' not found. Available contacts: {', '.join(list(self.contacts.keys())[:5])}"
                
        except Exception as e:
            return f"Error sending WhatsApp message: {str(e)}"
    
    def send_whatsapp_to_number(self, phone_number: str, message: str) -> str:
        """Send WhatsApp message to a phone number directly"""
        try:
            # Ensure phone number has country code
            if not phone_number.startswith('+'):
                phone_number = '+91' + phone_number.replace(' ', '')
            
            # Get current time and add 2 minutes
            now = datetime.datetime.now()
            hour = now.hour
            minute = now.minute + 2
            
            if minute >= 60:
                minute -= 60
                hour += 1
            
            print(f"Sending WhatsApp message to {phone_number}...")
            kit.sendwhatmsg(phone_number, message, hour, minute)
            
            return f"WhatsApp message scheduled to {phone_number}. WhatsApp Web will open in 2 minutes."
            
        except Exception as e:
            return f"Error sending WhatsApp message: {str(e)}"
    
    def send_whatsapp_file(self, contact_name: str, file_path: str) -> str:
        """Send a file via WhatsApp"""
        try:
            # Normalize contact name
            contact_name = contact_name.lower().strip()
            
            # Check if contact exists
            if contact_name in self.contacts:
                phone_number = self.contacts[contact_name]
            else:
                return f"Contact '{contact_name}' not found. Available contacts: {', '.join(list(self.contacts.keys())[:5])}"
            
            # Check if file exists
            if not os.path.exists(file_path):
                # Try common locations
                desktop = os.path.join(os.path.expanduser("~"), "Desktop", file_path)
                downloads = os.path.join(os.path.expanduser("~"), "Downloads", file_path)
                pictures = os.path.join(os.path.expanduser("~"), "Pictures", file_path)
                
                if os.path.exists(desktop):
                    file_path = desktop
                elif os.path.exists(downloads):
                    file_path = downloads
                elif os.path.exists(pictures):
                    file_path = pictures
                else:
                    return f"File not found: {file_path}. Please provide full path or place file on Desktop/Downloads/Pictures."
            
            # Get current time and add 3 minutes for safety
            now = datetime.datetime.now()
            hour = now.hour
            minute = now.minute + 3
            
            if minute >= 60:
                minute -= 60
                hour += 1
            if hour >= 24:
                hour = 0
            
            # Send file using pywhatkit
            print(f"Sending file to {contact_name} ({phone_number})...")
            kit.sendwhats_image(phone_number, file_path, "", hour, minute)
            
            return f"File scheduled to send to {contact_name}. WhatsApp Web will open in 3 minutes."
            
        except Exception as e:
            return f"Error sending file: {str(e)}"
    
    def send_whatsapp_file_to_number(self, phone_number: str, file_path: str) -> str:
        """Send a file via WhatsApp to a phone number"""
        try:
            # Ensure phone number has country code
            if not phone_number.startswith('+'):
                phone_number = '+91' + phone_number.replace(' ', '')
            
            # Check if file exists
            if not os.path.exists(file_path):
                # Try common locations
                desktop = os.path.join(os.path.expanduser("~"), "Desktop", file_path)
                downloads = os.path.join(os.path.expanduser("~"), "Downloads", file_path)
                pictures = os.path.join(os.path.expanduser("~"), "Pictures", file_path)
                
                if os.path.exists(desktop):
                    file_path = desktop
                elif os.path.exists(downloads):
                    file_path = downloads
                elif os.path.exists(pictures):
                    file_path = pictures
                else:
                    return f"File not found: {file_path}"
            
            # Get current time and add 3 minutes
            now = datetime.datetime.now()
            hour = now.hour
            minute = now.minute + 3
            
            if minute >= 60:
                minute -= 60
                hour += 1
            if hour >= 24:
                hour = 0
            
            print(f"Sending file to {phone_number}...")
            kit.sendwhats_image(phone_number, file_path, "", hour, minute)
            
            return f"File scheduled to send to {phone_number}. WhatsApp Web will open in 3 minutes."
            
        except Exception as e:
            return f"Error sending file: {str(e)}"
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take a screenshot and save it"""
        try:
            if filename is None:
                # Generate filename with timestamp
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            # Ensure filename has .png extension
            if not filename.endswith('.png'):
                filename += '.png'
            
            # Take screenshot
            screenshot = pyautogui.screenshot()
            
            # Save to Desktop or current directory
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if os.path.exists(desktop):
                filepath = os.path.join(desktop, filename)
            else:
                filepath = filename
            
            screenshot.save(filepath)
            
            return f"Screenshot saved as {filepath}"
            
        except Exception as e:
            return f"Error taking screenshot: {str(e)}"
    
    def get_system_info(self) -> str:
        """Get system information"""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used = memory.used / (1024 ** 3)  # Convert to GB
            memory_total = memory.total / (1024 ** 3)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free = disk.free / (1024 ** 3)
            
            info = (
                f"System Info: "
                f"CPU: {cpu_percent}%, "
                f"RAM: {memory_percent}% ({memory_used:.1f}GB / {memory_total:.1f}GB), "
                f"Disk: {disk_percent}% used, {disk_free:.1f}GB free"
            )
            return info
            
        except ImportError:
            return "System info requires psutil. Install with: pip install psutil"
        except Exception as e:
            return f"Error getting system info: {str(e)}"
    
    def set_volume(self, level: int) -> str:
        """Set system volume (0-100)"""
        try:
            if self.system_platform == "Windows":
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
                
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))
                
                # Set volume (0.0 to 1.0)
                volume.SetMasterVolumeLevelScalar(level / 100, None)
                return f"Volume set to {level}%"
            else:
                return "Volume control is currently only supported on Windows"
                
        except ImportError:
            return "Volume control requires pycaw. Install with: pip install pycaw comtypes"
        except Exception as e:
            return f"Error setting volume: {str(e)}"
    
    def lock_screen(self) -> str:
        """Lock the computer screen"""
        try:
            if self.system_platform == "Windows":
                os.system("rundll32.exe user32.dll,LockWorkStation")
                return "Locking screen..."
            elif self.system_platform == "Darwin":
                os.system("pmset displaysleepnow")
                return "Locking screen..."
            else:
                os.system("gnome-screensaver-command -l")
                return "Locking screen..."
        except Exception as e:
            return f"Error locking screen: {str(e)}"
    
    def shutdown_system(self) -> str:
        """Shutdown the computer"""
        try:
            if self.system_platform == "Windows":
                os.system("shutdown /s /t 30")
                return "System will shutdown in 30 seconds. Say 'cancel shutdown' to abort."
            elif self.system_platform == "Darwin":
                os.system("sudo shutdown -h +1")
                return "System will shutdown in 1 minute."
            else:
                os.system("shutdown -h +1")
                return "System will shutdown in 1 minute."
        except Exception as e:
            return f"Error shutting down: {str(e)}"
    
    def restart_system(self) -> str:
        """Restart the computer"""
        try:
            if self.system_platform == "Windows":
                os.system("shutdown /r /t 30")
                return "System will restart in 30 seconds."
            elif self.system_platform == "Darwin":
                os.system("sudo shutdown -r +1")
                return "System will restart in 1 minute."
            else:
                os.system("shutdown -r +1")
                return "System will restart in 1 minute."
        except Exception as e:
            return f"Error restarting: {str(e)}"
    
    def sleep_system(self) -> str:
        """Put the computer to sleep"""
        try:
            if self.system_platform == "Windows":
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
                return "Putting system to sleep..."
            elif self.system_platform == "Darwin":
                os.system("pmset sleepnow")
                return "Putting system to sleep..."
            else:
                os.system("systemctl suspend")
                return "Putting system to sleep..."
        except Exception as e:
            return f"Error putting system to sleep: {str(e)}"
    
    def hibernate_system(self) -> str:
        """Hibernate the computer"""
        try:
            if self.system_platform == "Windows":
                os.system("shutdown /h")
                return "Hibernating system..."
            else:
                return "Hibernate is only supported on Windows"
        except Exception as e:
            return f"Error hibernating: {str(e)}"
    
    def cancel_shutdown(self) -> str:
        """Cancel scheduled shutdown"""
        try:
            if self.system_platform == "Windows":
                os.system("shutdown /a")
                return "Shutdown cancelled."
            else:
                return "Shutdown cancellation is only supported on Windows through this command."
        except Exception as e:
            return f"Error cancelling shutdown: {str(e)}"
    
    def switch_tab(self, direction: str = "next") -> str:
        """Switch browser tabs"""
        try:
            if direction == "next":
                # Ctrl + Tab (next tab)
                pyautogui.hotkey('ctrl', 'tab')
                return "Switching to next tab"
            elif direction == "previous" or direction == "prev":
                # Ctrl + Shift + Tab (previous tab)
                pyautogui.hotkey('ctrl', 'shift', 'tab')
                return "Switching to previous tab"
            else:
                return "Please specify 'next' or 'previous' tab"
        except Exception as e:
            return f"Error switching tab: {str(e)}"
    
    def close_tab(self) -> str:
        """Close current browser tab"""
        try:
            pyautogui.hotkey('ctrl', 'w')
            return "Closing current tab"
        except Exception as e:
            return f"Error closing tab: {str(e)}"
    
    def new_tab(self) -> str:
        """Open new browser tab"""
        try:
            pyautogui.hotkey('ctrl', 't')
            return "Opening new tab"
        except Exception as e:
            return f"Error opening new tab: {str(e)}"
    
    def switch_window(self) -> str:
        """Switch between windows"""
        try:
            pyautogui.hotkey('alt', 'tab')
            return "Switching window"
        except Exception as e:
            return f"Error switching window: {str(e)}"
    
    def minimize_window(self) -> str:
        """Minimize current window"""
        try:
            pyautogui.hotkey('win', 'down')
            return "Minimizing window"
        except Exception as e:
            return f"Error minimizing window: {str(e)}"
    
    def maximize_window(self) -> str:
        """Maximize current window"""
        try:
            pyautogui.hotkey('win', 'up')
            return "Maximizing window"
        except Exception as e:
            return f"Error maximizing window: {str(e)}"
    
    def show_desktop(self) -> str:
        """Show desktop (minimize all windows)"""
        try:
            if self.system_platform == "Windows":
                pyautogui.hotkey('win', 'd')
            elif self.system_platform == "Darwin":
                pyautogui.hotkey('fn', 'f11')
            else:
                pyautogui.hotkey('ctrl', 'alt', 'd')
            return "Showing desktop"
        except Exception as e:
            return f"Error showing desktop: {str(e)}"
    
    def type_text(self, text: str) -> str:
        """Type the given text"""
        try:
            # Small delay to allow user to click where they want to type
            time.sleep(1)
            
            # Type the text
            pyautogui.write(text, interval=0.05)
            
            return f"Typed: {text}"
        except Exception as e:
            return f"Error typing text: {str(e)}"
    
    def press_enter(self) -> str:
        """Press Enter key"""
        try:
            pyautogui.press('enter')
            return "Pressed Enter"
        except Exception as e:
            return f"Error pressing Enter: {str(e)}"
    
    def press_backspace(self, count: int = 1) -> str:
        """Press Backspace key"""
        try:
            for _ in range(count):
                pyautogui.press('backspace')
            return f"Pressed Backspace {count} time(s)"
        except Exception as e:
            return f"Error pressing Backspace: {str(e)}"
    
    def select_all(self) -> str:
        """Select all text (Ctrl+A)"""
        try:
            pyautogui.hotkey('ctrl', 'a')
            return "Selected all text"
        except Exception as e:
            return f"Error selecting all: {str(e)}"
    
    def copy_text(self) -> str:
        """Copy selected text (Ctrl+C)"""
        try:
            pyautogui.hotkey('ctrl', 'c')
            return "Copied text"
        except Exception as e:
            return f"Error copying: {str(e)}"
    
    def paste_text(self) -> str:
        """Paste text (Ctrl+V)"""
        try:
            pyautogui.hotkey('ctrl', 'v')
            return "Pasted text"
        except Exception as e:
            return f"Error pasting: {str(e)}"
    
    def cut_text(self) -> str:
        """Cut selected text (Ctrl+X)"""
        try:
            pyautogui.hotkey('ctrl', 'x')
            return "Cut text"
        except Exception as e:
            return f"Error cutting: {str(e)}"
    
    def undo(self) -> str:
        """Undo last action (Ctrl+Z)"""
        try:
            pyautogui.hotkey('ctrl', 'z')
            return "Undone last action"
        except Exception as e:
            return f"Error undoing: {str(e)}"
    
    def redo(self) -> str:
        """Redo last action (Ctrl+Y)"""
        try:
            pyautogui.hotkey('ctrl', 'y')
            return "Redone last action"
        except Exception as e:
            return f"Error redoing: {str(e)}"
    
    def search_wikipedia(self, query: str) -> str:
        """Search Wikipedia and return summary"""
        try:
            wiki = wikipediaapi.Wikipedia('JARVIS/1.0', 'en')
            page = wiki.page(query)
            
            if page.exists():
                # Get first 3 sentences of summary
                summary = page.summary.split('.')[:3]
                summary_text = '. '.join(summary) + '.'
                
                # Also open the page in browser
                webbrowser.open(page.fullurl)
                
                return f"Wikipedia: {summary_text}"
            else:
                return f"No Wikipedia article found for '{query}'. Try a different search term."
                
        except Exception as e:
            return f"Error searching Wikipedia: {str(e)}"
    
    def open_youtube(self) -> str:
        """Open YouTube homepage"""
        try:
            webbrowser.open("https://www.youtube.com")
            return "Opening YouTube"
        except Exception as e:
            return f"Error opening YouTube: {str(e)}"
    
    def play_youtube_video(self, query: str) -> str:
        """Play a video on YouTube"""
        try:
            # Use pywhatkit to play video directly
            kit.playonyt(query)
            return f"Playing '{query}' on YouTube"
        except Exception as e:
            return f"Error playing YouTube video: {str(e)}"
    
    def search_youtube(self, query: str) -> str:
        """Search YouTube for videos"""
        try:
            search_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(search_url)
            return f"Searching YouTube for '{query}'"
        except Exception as e:
            return f"Error searching YouTube: {str(e)}"
    
    def chat_with_ai(self, message: str) -> str:
        """Chat with Gemini AI"""
        if not self.model:
            return "AI is not available. Please check your API key."
        
        try:
            response = self.chat.send_message(message)
            return response.text
        except Exception as e:
            return f"AI Error: {str(e)}"
    
    def process_command(self, command: str) -> str:
        """Process user command and return response"""
        command = command.lower().strip()
        
        # Typing/Dictation (check FIRST before other commands)
        if ("write" in command or "type" in command) and not any(word in command for word in ["rewrite", "overwrite"]):
            # Extract text to type
            text_to_type = command.replace("write", "").replace("type", "").strip()
            if text_to_type:
                return self.type_text(text_to_type)
            else:
                return "Please specify what to write. Example: 'write Hello World'"
        
        # WhatsApp message (check this BEFORE greeting)
        elif ("send" in command or "whatsapp" in command) and ("message" in command or "saying" in command or "file" in command or "image" in command or "photo" in command or "document" in command):
            try:
                # Send file
                if "file" in command or "image" in command or "photo" in command or "document" in command or "pdf" in command:
                    # Parse: "send file NAME.ext to CONTACT"
                    if " to " in command:
                        parts = command.split(" to ")
                        # Extract file name
                        file_part = parts[0]
                        for word in ["send", "file", "image", "photo", "document", "pdf", "whatsapp"]:
                            file_part = file_part.replace(word, "")
                        file_name = file_part.strip()
                        
                        # Extract contact
                        contact_name = parts[1].strip()
                        
                        if file_name and contact_name:
                            return self.send_whatsapp_file(contact_name, file_name)
                        else:
                            return "Please specify: 'send file FILENAME to CONTACT'"
                    else:
                        return "Please say: 'send file FILENAME to CONTACT'"
                
                # Send message
                elif " to " in command and " saying " in command:
                    parts = command.split(" to ")
                    contact_part = parts[1].split(" saying ")[0].strip()
                    message_part = parts[1].split(" saying ")[1].strip()
                    
                    return self.send_whatsapp_message(contact_part, message_part)
                
                # Send message to number
                elif " to " in command and ("message" in command or "msg" in command):
                    parts = command.split(" to ")
                    if len(parts) > 1:
                        rest = parts[1]
                        # Extract number and message
                        words = rest.split()
                        phone = words[0]
                        if "message" in rest:
                            message = rest.split("message")[1].strip()
                        elif "msg" in rest:
                            message = rest.split("msg")[1].strip()
                        else:
                            message = " ".join(words[1:])
                        
                        return self.send_whatsapp_to_number(phone, message)
                else:
                    return "Please say: 'send message to NAME saying YOUR MESSAGE' or 'send file FILENAME to CONTACT'"
            except Exception as e:
                return f"Error parsing WhatsApp command: {str(e)}"
        
        # Greeting
        elif any(word in command for word in ["hello", "hi", "hey", "jarvis"]):
            return "Hello! How can I assist you today?"
        
        # Time
        elif "time" in command:
            return self.get_time()
        
        # Date
        elif "date" in command or "today" in command:
            return self.get_date()
        
        # Weather
        elif "weather" in command:
            city = ""
            if "in" in command:
                city = command.split("in")[-1].strip()
            return self.get_weather(city)
        
        # Screenshot
        elif "screenshot" in command or "take screenshot" in command or "capture screen" in command:
            return self.take_screenshot()
        
        # System info
        elif "system info" in command or "system status" in command:
            return self.get_system_info()
        
        # Volume control
        elif "volume" in command or "set volume" in command:
            try:
                # Extract volume level
                words = command.split()
                for i, word in enumerate(words):
                    if word.isdigit():
                        level = int(word)
                        return self.set_volume(level)
                return "Please specify volume level (0-100). Example: 'set volume 50'"
            except:
                return "Error parsing volume command"
        
        # Lock screen
        elif "lock" in command and ("screen" in command or "computer" in command):
            return self.lock_screen()
        
        # Sleep
        elif "sleep" in command and ("system" in command or "computer" in command or "laptop" in command):
            return self.sleep_system()
        
        # Hibernate
        elif "hibernate" in command:
            return self.hibernate_system()
        
        # Shutdown
        elif "shutdown" in command or "shut down" in command or "power off" in command or "poweroff" in command:
            if "cancel" in command:
                return self.cancel_shutdown()
            else:
                return self.shutdown_system()
        
        # Restart
        elif "restart" in command or "reboot" in command:
            return self.restart_system()
        
        # Tab switching
        elif "next tab" in command or "switch tab" in command:
            return self.switch_tab("next")
        
        elif "previous tab" in command or "prev tab" in command:
            return self.switch_tab("previous")
        
        elif "close tab" in command:
            return self.close_tab()
        
        elif "new tab" in command or "open tab" in command:
            return self.new_tab()
        
        # Window management
        elif "switch window" in command or "next window" in command:
            return self.switch_window()
        
        elif "minimize window" in command or "minimize" in command:
            return self.minimize_window()
        
        elif "maximize window" in command or "maximize" in command:
            return self.maximize_window()
        
        elif "show desktop" in command or "desktop" in command:
            return self.show_desktop()
        
        # Keyboard shortcuts
        elif "press enter" in command or command.strip() == "enter":
            return self.press_enter()
        
        elif "backspace" in command:
            # Check if number specified
            words = command.split()
            count = 1
            for word in words:
                if word.isdigit():
                    count = int(word)
                    break
            return self.press_backspace(count)
        
        elif "select all" in command:
            return self.select_all()
        
        elif "copy" in command and "close" not in command:
            return self.copy_text()
        
        elif "paste" in command:
            return self.paste_text()
        
        elif "cut" in command:
            return self.cut_text()
        
        elif "undo" in command:
            return self.undo()
        
        elif "redo" in command:
            return self.redo()
        
        # YouTube - Enhanced (check BEFORE open application)
        elif "youtube" in command:
            if "open youtube" in command or command.strip() == "youtube":
                return self.open_youtube()
            elif "play" in command:
                # Extract video query
                query = command.replace("youtube", "").replace("play", "").replace("on youtube", "").replace("video", "").strip()
                if query:
                    return self.play_youtube_video(query)
                else:
                    return "Please specify what to play on YouTube"
            elif "search" in command:
                query = command.replace("youtube", "").replace("search", "").replace("on youtube", "").replace("for", "").strip()
                if query:
                    return self.search_youtube(query)
                else:
                    return "Please specify what to search on YouTube"
            else:
                return self.open_youtube()
        
        # Play video (shortcut for YouTube)
        elif "play" in command and not any(word in command for word in ["open", "close"]):
            query = command.replace("play", "").replace("video", "").replace("on youtube", "").strip()
            if query:
                return self.play_youtube_video(query)
            else:
                return "Please specify what to play"
        
        # Open application
        elif "open" in command:
            app_name = command.replace("open", "").strip()
            return self.open_application(app_name)
        
        # Close application
        elif "close" in command:
            app_name = command.replace("close", "").strip()
            return self.close_application(app_name)
        
        # Web search
        elif "search" in command or "google" in command:
            query = command.replace("search", "").replace("google", "").replace("for", "").strip()
            return self.search_web(query)
        
        # Wikipedia
        elif "wikipedia" in command or "wiki" in command:
            query = command.replace("wikipedia", "").replace("wiki", "").replace("search", "").replace("for", "").strip()
            if query:
                return self.search_wikipedia(query)
            else:
                return "Please specify what to search on Wikipedia"
        
        # Simple math (basic calculator)
        elif any(op in command for op in ['+', '-', '*', '/', 'plus', 'minus', 'times', 'divided']):
            try:
                # Replace words with operators
                math_cmd = command.replace('plus', '+').replace('minus', '-')
                math_cmd = math_cmd.replace('times', '*').replace('multiplied by', '*')
                math_cmd = math_cmd.replace('divided by', '/').replace('what is', '').replace('?', '')
                math_cmd = math_cmd.strip()
                
                # Evaluate safely
                result = eval(math_cmd, {"__builtins__": {}}, {})
                return f"The answer is {result}"
            except:
                # If math fails, ask AI
                return self.chat_with_ai(command)
        
        # Exit/Quit
        elif any(word in command for word in ["exit", "quit", "goodbye", "bye"]):
            return "QUIT"
        
        # Help
        elif "help" in command or "what can you do" in command:
            return self.get_help_message()
        
        # Default: Ask AI
        else:
            return self.chat_with_ai(command)
    
    def get_help_message(self) -> str:
        """Return help message with available commands"""
        help_text = """
I can help you with:
• Open/Close applications (e.g., "open chrome", "close notepad")
• Web search (e.g., "search Python tutorials")
• Wikipedia (e.g., "wikipedia Python programming")
• YouTube: Open, Play videos, Search
• Weather updates (e.g., "weather in London")
• Time and date (e.g., "what time is it?")
• WhatsApp messages (e.g., "send message to Soumya saying Hello")
• WhatsApp files (e.g., "send file photo.jpg to Soumya")
• Typing/Dictation (e.g., "write Hello World")
• Keyboard shortcuts: Enter, Backspace, Copy, Paste, Cut, Undo, Redo
• Screenshot (e.g., "take screenshot")
• System info (e.g., "system status")
• Volume control (e.g., "set volume 50")
• Power: Lock, Sleep, Hibernate, Shutdown, Restart
• Tab control: Next tab, Previous tab, Close tab, New tab
• Window control: Switch window, Minimize, Maximize, Show desktop
• Math calculations (e.g., "what is 2 + 2")
• General questions (powered by AI)
• And much more! Just ask me anything.
        """
        return help_text.strip()


# Test function
if __name__ == "__main__":
    print("=" * 50)
    print("JARVIS Backend Test")
    print("=" * 50)
    
    # Initialize JARVIS
    API_KEY = "AIzaSyDi1pyCQyCen--a1dkna1iAm8JP1M_-yXA"
    jarvis = JarvisBackend(API_KEY)
    
    # Test commands
    test_commands = [
        "Hello JARVIS",
        "What time is it?",
        "What is Python?",
    ]
    
    for cmd in test_commands:
        print(f"\n> {cmd}")
        response = jarvis.process_command(cmd)
        jarvis.speak(response)
        time.sleep(1)
