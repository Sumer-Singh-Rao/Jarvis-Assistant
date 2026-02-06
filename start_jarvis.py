"""
JARVIS Quick Launcher
Automatically installs dependencies and starts JARVIS
"""

import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("=" * 60)
    print("🤖 JARVIS Quick Start")
    print("=" * 60)
    print("\n📦 Checking dependencies...")
    
    try:
        # Try importing required packages
        import google.generativeai
        import pyttsx3
        import speech_recognition
        print("✓ All dependencies installed!")
        return True
    except ImportError:
        print("\n⚠️  Missing dependencies detected.")
        print("📥 Installing required packages...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print("✓ Dependencies installed successfully!")
            return True
        except Exception as e:
            print(f"✗ Error installing dependencies: {e}")
            print("\n💡 Please install manually:")
            print("   pip install -r requirements.txt")
            return False

def check_pyaudio():
    """Check if PyAudio is installed"""
    try:
        import pyaudio
        return True
    except ImportError:
        print("\n⚠️  PyAudio not found!")
        print("\n📝 Installation instructions:")
        
        if sys.platform == "win32":
            print("   Windows: Download from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
        elif sys.platform == "darwin":
            print("   macOS: brew install portaudio && pip install pyaudio")
        else:
            print("   Linux: sudo apt-get install python3-pyaudio portaudio19-dev")
        
        print("\n🔊 Voice input will not work without PyAudio.")
        response = input("Continue anyway? (y/n): ")
        return response.lower() == 'y'

def main():
    """Main launcher function"""
    
    # Install dependencies
    if not install_requirements():
        input("\nPress Enter to exit...")
        return
    
    # Check PyAudio
    has_pyaudio = check_pyaudio()
    
    # Choose mode
    print("\n" + "=" * 60)
    print("🚀 Launch JARVIS")
    print("=" * 60)
    print("\nSelect mode:")
    print("  1. GUI Mode (Recommended)")
    print("  2. Backend Test Mode")
    print("  3. Exit")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🎨 Starting GUI...")
        if not has_pyaudio:
            print("⚠️  Voice input disabled (PyAudio not installed)")
        try:
            import jarvis_frontend
            app = jarvis_frontend.JarvisGUI("AIzaSyDi1pyCQyCen--a1dkna1iAm8JP1M_-yXA")
            app.run()
        except Exception as e:
            print(f"\n✗ Error starting GUI: {e}")
            input("\nPress Enter to exit...")
    
    elif choice == "2":
        print("\n🔧 Starting backend test...")
        try:
            import jarvis_backend
            jarvis = jarvis_backend.JarvisBackend(
                "AIzaSyDi1pyCQyCen--a1dkna1iAm8JP1M_-yXA",
                weather_api_key="bd5e378503939ddaee76f12ad7a97608"
            )
            
            print("\n" + "=" * 60)
            print("✓ Backend initialized successfully!")
            print("=" * 60)
            print("\n💬 Type your commands (or 'quit' to exit):")
            
            while True:
                cmd = input("\nYou: ").strip()
                if cmd.lower() in ['quit', 'exit', 'bye']:
                    print("JARVIS: Goodbye!")
                    break
                
                if cmd:
                    response = jarvis.process_command(cmd)
                    print(f"JARVIS: {response}")
        
        except Exception as e:
            print(f"\n✗ Error: {e}")
            input("\nPress Enter to exit...")
    
    else:
        print("\n👋 Goodbye!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        input("\nPress Enter to exit...")
