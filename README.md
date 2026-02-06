# 🤖 JARVIS - AI Assistant

**J**ust **A** **R**ather **V**ery **I**ntelligent **S**ystem

A fully functional AI assistant inspired by Iron Man's JARVIS, powered by Google's Gemini AI.

## ✨ Features

### 🎯 Core Capabilities
- **🎤 Voice Recognition** - Speak commands naturally
- **🔊 Text-to-Speech** - JARVIS responds with voice
- **🤖 AI Conversations** - Powered by Google Gemini AI
- **💬 General Chat** - Ask any question, explain concepts
- **📱 App Control** - Open and close applications
- **🔍 Web Search** - Search Google instantly
- **🌤️ Weather Updates** - Real-time weather information
- **⏰ Time & Date** - Current time and date
- **🎥 YouTube** - Play videos directly
- **💻 Modern GUI** - Beautiful, user-friendly interface

### 🎨 Interface Features
- **Dark Theme** - Easy on the eyes
- **Real-time Status** - Visual indicators for system state
- **Chat History** - Scrollable conversation log
- **Multiple Input Methods** - Voice or text
- **Colored Messages** - Easy to distinguish speakers

## 📋 Requirements

- Python 3.7 or higher
- Windows, macOS, or Linux
- Microphone (for voice input)
- Internet connection
- Google Gemini API key (get free at https://makersuite.google.com/app/apikey)
- OpenWeatherMap API key (get free at https://openweathermap.org/api)

## 🚀 Installation

### Step 1: Install Python
Make sure Python 3.7+ is installed:
```bash
python --version
```

### Step 2: Clone the Repository
```bash
git clone https://github.com/Sumer-Singh-Rao/Jarvis-Assistant.git
cd Jarvis-Assistant
```

### Step 3: Set Up API Keys
1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```
2. Edit `.env` and add your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   WEATHER_API_KEY=your_openweathermap_api_key_here
   ```

### Step 4: Install Dependencies

#### On Windows:
```bash
pip install -r requirements.txt
```

**Note for PyAudio on Windows:**
If PyAudio installation fails, download the wheel file:
1. Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Download the appropriate `.whl` file for your Python version
3. Install: `pip install path/to/downloaded/PyAudio.whl`

#### On macOS:
```bash
# Install portaudio first
brew install portaudio

# Then install requirements
pip install -r requirements.txt
```

#### On Linux:
```bash
# Install dependencies
sudo apt-get update
sudo apt-get install python3-pyaudio portaudio19-dev espeak

# Then install requirements
pip install -r requirements.txt
```

### Step 5: Verify Installation
```bash
python jarvis_backend.py
```

## 🎮 Usage

### Starting JARVIS

**Method 1: GUI Mode (Recommended)**
```bash
python jarvis_frontend.py
```

**Method 2: Backend Only (Testing)**
```bash
python jarvis_backend.py
```

### 🎤 Voice Commands Examples

**General Conversation:**
- "Hello JARVIS"
- "How are you?"
- "Tell me a joke"
- "Explain quantum physics"
- "What is machine learning?"

**Time & Date:**
- "What time is it?"
- "What's today's date?"

**Weather:**
- "What's the weather?"
- "Weather in London"
- "What's the temperature in Tokyo?"

**Applications:**
- "Open Chrome"
- "Open Notepad"
- "Open Calculator"
- "Close Chrome"
- "Open File Explorer"

**Web Search:**
- "Search Python tutorials"
- "Google artificial intelligence"
- "Search best restaurants near me"

**YouTube:**
- "Play music on YouTube"
- "Play Avengers trailer on YouTube"

**Help & Exit:**
- "Help" or "What can you do?"
- "Exit" or "Goodbye"

### ⌨️ Text Commands

You can also type any of the above commands in the text input box.

## 📁 File Structure

```
jarvis/
├── jarvis_frontend.py    # GUI Interface
├── jarvis_backend.py     # Core Engine
├── requirements.txt      # Dependencies
└── README.md            # This file
```

## 🔧 Customization

### Change Voice Settings
Edit `jarvis_backend.py`:
```python
def setup_speech_engine(self):
    self.engine.setProperty('rate', 180)    # Speed (change this)
    self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
```

### Add More Applications
Edit the `get_system_apps()` method in `jarvis_backend.py`:
```python
def get_system_apps(self):
    if self.system_platform == "Windows":
        return {
            "your_app": "path/to/app.exe",
            # Add more apps here
        }
```

### Change GUI Colors
Edit `jarvis_frontend.py` color codes:
- Background: `#0a0e27`
- Accent: `#00d4ff`
- Chat background: `#1a1f3a`

## 🛠️ Troubleshooting

### Voice Recognition Not Working
1. Check microphone permissions
2. Test microphone in system settings
3. Install latest PyAudio version
4. Reduce background noise

### Text-to-Speech Issues
1. Windows: Check if SAPI5 voices are installed
2. macOS: Check System Preferences > Accessibility > Speech
3. Linux: Install espeak: `sudo apt-get install espeak`

### API Errors
1. Verify internet connection
2. Check if Gemini API key is valid
3. Review API quota limits

### Application Won't Open
1. Ensure application is installed
2. Try full application name
3. Check application path in `get_system_apps()`

## 🎯 Advanced Features

### Custom Commands
Add custom logic in `process_command()` method:
```python
def process_command(self, command: str) -> str:
    if "your custom command" in command:
        # Your custom logic
        return "Custom response"
```

### Integration with Other APIs
You can extend JARVIS with:
- Email automation
- Calendar management
- Smart home control
- News aggregation
- Social media integration

## 📝 Notes

- Voice recognition requires internet (uses Google Speech API)
- Weather data from wttr.in (no API key needed)
- AI responses powered by Google Gemini
- Some apps may require administrator privileges

## 🔐 Security

- **NEVER commit your `.env` file to GitHub**
- API keys are stored in `.env` (already in .gitignore)
- Get your free API keys:
  - Gemini AI: https://makersuite.google.com/app/apikey
  - Weather: https://openweathermap.org/api
- For production use, consider using environment variables or secret management services

## 🤝 Contributing

Feel free to:
- Add new features
- Improve voice recognition
- Enhance UI/UX
- Add more commands
- Fix bugs

## 📜 License

This is a personal project for educational purposes.

## 🙏 Credits

- **Google Gemini AI** - For powerful AI responses
- **pyttsx3** - Text-to-speech engine
- **SpeechRecognition** - Voice input
- **Iron Man** - For the inspiration!

## 📧 Support

If you encounter issues:
1. Check the troubleshooting section
2. Verify all dependencies are installed
3. Test with simple commands first
4. Check console for error messages

---

**Enjoy your personal JARVIS! 🚀**

*"Sometimes you gotta run before you can walk." - Tony Stark*
