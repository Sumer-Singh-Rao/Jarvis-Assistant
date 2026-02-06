"""
JARVIS Frontend - Animated Interface with Glowing Orb
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import queue
import sys
import math
from datetime import datetime

# Import backend
try:
    from jarvis_backend import JarvisBackend
except ImportError:
    print("Error: jarvis_backend.py not found!")
    sys.exit(1)


class JarvisGUI:
    """Animated GUI for JARVIS with glowing orb"""
    
    def __init__(self, api_key: str):
        """Initialize the GUI"""
        self.api_key = api_key
        self.window = tk.Tk()
        self.window.title("J.A.R.V.I.S")
        self.window.geometry("1000x800")
        self.window.configure(bg="#000000")
        
        # Initialize backend
        self.jarvis = None
        self.message_queue = queue.Queue()
        self.is_listening = False
        
        # Animation variables
        self.orb_angle = 0
        self.orb_pulse = 0
        self.animation_running = True
        
        # Setup UI
        self.setup_ui()
        
        # Initialize backend
        self.init_backend()
        
        # Start animations
        self.animate_orb()
        
        # Start message processor
        self.process_messages()
        
    def setup_ui(self):
        """Create the animated user interface"""
        
        # Top section - Animated Orb
        orb_frame = tk.Frame(self.window, bg="#000000", height=400)
        orb_frame.pack(fill=tk.BOTH, expand=True)
        orb_frame.pack_propagate(False)
        
        # Canvas for animated orb
        self.orb_canvas = tk.Canvas(
            orb_frame,
            bg="#000000",
            highlightthickness=0
        )
        self.orb_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Status text above orb
        self.status_label = tk.Label(
            orb_frame,
            text="INITIALIZING...",
            font=("Arial", 14, "bold"),
            fg="#00d4ff",
            bg="#000000"
        )
        self.status_label.place(relx=0.5, rely=0.15, anchor=tk.CENTER)
        
        # Response text below orb
        self.response_label = tk.Label(
            orb_frame,
            text="",
            font=("Arial", 12),
            fg="#ffffff",
            bg="#000000",
            wraplength=700,
            justify=tk.CENTER
        )
        self.response_label.place(relx=0.5, rely=0.75, anchor=tk.CENTER)
        
        # Bottom section - Input and controls
        bottom_frame = tk.Frame(self.window, bg="#000000")
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=20)
        
        # Input container
        input_container = tk.Frame(bottom_frame, bg="#000000")
        input_container.pack(pady=10)
        
        # Input frame with border
        input_frame = tk.Frame(
            input_container,
            bg="#1a1a3e",
            highlightbackground="#00d4ff",
            highlightthickness=2
        )
        input_frame.pack(padx=40)
        
        # Text Input
        self.command_entry = tk.Entry(
            input_frame,
            font=("Arial", 14),
            bg="#1a1a3e",
            fg="#ffffff",
            insertbackground="#00d4ff",
            relief=tk.FLAT,
            bd=0,
            width=60
        )
        self.command_entry.pack(side=tk.LEFT, padx=15, pady=15)
        self.command_entry.bind("<Return>", lambda e: self.send_text_command())
        
        # Send button
        send_btn = tk.Button(
            input_frame,
            text="→",
            font=("Arial", 16, "bold"),
            bg="#00d4ff",
            fg="#000000",
            activebackground="#00aacc",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=self.send_text_command,
            width=3
        )
        send_btn.pack(side=tk.RIGHT, padx=10)
        
        # Control buttons
        button_frame = tk.Frame(bottom_frame, bg="#000000")
        button_frame.pack(pady=10)
        
        # Voice button
        self.voice_button = tk.Button(
            button_frame,
            text="🎤 VOICE",
            font=("Arial", 11, "bold"),
            bg="#1a1a3e",
            fg="#00d4ff",
            activebackground="#2a2a4e",
            activeforeground="#00d4ff",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=self.toggle_voice_input,
            padx=20,
            pady=10
        )
        self.voice_button.pack(side=tk.LEFT, padx=5)
        
        # Chat history button
        chat_btn = tk.Button(
            button_frame,
            text="💬 HISTORY",
            font=("Arial", 11, "bold"),
            bg="#1a1a3e",
            fg="#00d4ff",
            activebackground="#2a2a4e",
            activeforeground="#00d4ff",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=self.show_history,
            padx=20,
            pady=10
        )
        chat_btn.pack(side=tk.LEFT, padx=5)
        
        # Help button
        help_btn = tk.Button(
            button_frame,
            text="❓ HELP",
            font=("Arial", 11, "bold"),
            bg="#1a1a3e",
            fg="#00d4ff",
            activebackground="#2a2a4e",
            activeforeground="#00d4ff",
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=self.show_help,
            padx=20,
            pady=10
        )
        help_btn.pack(side=tk.LEFT, padx=5)
        
        # Hidden chat history
        self.chat_history = []
        
    def animate_orb(self):
        """Animate the glowing orb"""
        if not self.animation_running:
            return
        
        self.orb_canvas.delete("all")
        
        # Get canvas center
        width = self.orb_canvas.winfo_width() or 1000
        height = self.orb_canvas.winfo_height() or 400
        cx, cy = width // 2, height // 2
        
        # Update animation variables
        self.orb_pulse += 0.08
        self.orb_angle += 0.05
        
        # Pulse effect
        pulse = math.sin(self.orb_pulse) * 15 + 100
        
        # Draw outer glow rings
        for i in range(5):
            radius = pulse + (i * 25)
            alpha_val = int(50 - (i * 8))
            color = f"#{alpha_val:02x}{alpha_val + 100:02x}ff"
            self.orb_canvas.create_oval(
                cx - radius, cy - radius,
                cx + radius, cy + radius,
                outline=color,
                width=2,
                fill=""
            )
        
        # Draw rotating particles
        for i in range(12):
            angle = self.orb_angle + (i * math.pi / 6)
            x = cx + math.cos(angle) * (pulse + 30)
            y = cy + math.sin(angle) * (pulse + 30)
            size = 4
            self.orb_canvas.create_oval(
                x - size, y - size,
                x + size, y + size,
                fill="#00d4ff",
                outline=""
            )
        
        # Draw core
        core_size = pulse * 0.6
        self.orb_canvas.create_oval(
            cx - core_size, cy - core_size,
            cx + core_size, cy + core_size,
            fill="#001a33",
            outline="#00d4ff",
            width=3
        )
        
        # Inner glow
        inner_size = core_size * 0.7
        self.orb_canvas.create_oval(
            cx - inner_size, cy - inner_size,
            cx + inner_size, cy + inner_size,
            fill="#003366",
            outline=""
        )
        
        # Center dot
        dot_size = 8
        self.orb_canvas.create_oval(
            cx - dot_size, cy - dot_size,
            cx + dot_size, cy + dot_size,
            fill="#00ffff",
            outline=""
        )
        
        # Schedule next frame
        self.window.after(30, self.animate_orb)
    
    def init_backend(self):
        """Initialize the backend"""
        def init_thread():
            try:
                self.jarvis = JarvisBackend(self.api_key)
                self.update_status("ONLINE - READY")
                self.show_response("All systems operational. How may I assist you?")
            except Exception as e:
                self.update_status("ERROR")
                self.show_response(f"Initialization error: {str(e)}")
        
        thread = threading.Thread(target=init_thread, daemon=True)
        thread.start()
    
    def update_status(self, text: str):
        """Update status text"""
        self.status_label.config(text=text)
    
    def show_response(self, text: str):
        """Show response text"""
        self.response_label.config(text=text)
        # Add to history
        self.chat_history.append(("JARVIS", text))
    
    def send_text_command(self):
        """Send text command"""
        command = self.command_entry.get().strip()
        
        if not command:
            return
        
        if not self.jarvis:
            messagebox.showwarning("Not Ready", "JARVIS is still initializing.")
            return
        
        # Clear entry
        self.command_entry.delete(0, tk.END)
        
        # Add to history
        self.chat_history.append(("YOU", command))
        self.show_response(f"You: {command}")
        
        # Process in thread
        def process():
            self.update_status("PROCESSING...")
            response = self.jarvis.process_command(command)
            
            if response == "QUIT":
                self.show_response("Goodbye! Shutting down...")
                self.window.after(2000, self.window.quit)
            else:
                self.show_response(response)
                # Speak response
                threading.Thread(
                    target=lambda: self.jarvis.speak(response),
                    daemon=True
                ).start()
            
            self.update_status("ONLINE - READY")
        
        thread = threading.Thread(target=process, daemon=True)
        thread.start()
    
    def toggle_voice_input(self):
        """Toggle voice input"""
        if not self.jarvis:
            messagebox.showwarning("Not Ready", "JARVIS is still initializing.")
            return
        
        if self.is_listening:
            self.is_listening = False
            self.voice_button.config(text="🎤 VOICE", bg="#1a1a3e")
            self.update_status("ONLINE - READY")
        else:
            self.is_listening = True
            self.voice_button.config(text="⏹️ STOP", bg="#ff4444")
            self.start_voice_input()
    
    def start_voice_input(self):
        """Start voice input"""
        def listen_thread():
            self.update_status("LISTENING...")
            self.show_response("Listening for your command...")
            
            command = self.jarvis.listen()
            
            if command and self.is_listening:
                self.chat_history.append(("YOU", command))
                self.show_response(f"You: {command}")
                self.update_status("PROCESSING...")
                
                response = self.jarvis.process_command(command)
                
                if response == "QUIT":
                    self.show_response("Goodbye! Shutting down...")
                    self.is_listening = False
                    self.window.after(2000, self.window.quit)
                else:
                    self.show_response(response)
                    self.jarvis.speak(response)
            
            if self.is_listening:
                self.update_status("LISTENING...")
                self.window.after(100, self.start_voice_input)
            else:
                self.update_status("ONLINE - READY")
        
        thread = threading.Thread(target=listen_thread, daemon=True)
        thread.start()
    
    def show_history(self):
        """Show chat history"""
        history_window = tk.Toplevel(self.window)
        history_window.title("Chat History")
        history_window.geometry("600x500")
        history_window.configure(bg="#0a0a1a")
        
        chat_display = scrolledtext.ScrolledText(
            history_window,
            font=("Consolas", 10),
            bg="#0a0a1a",
            fg="#ffffff",
            relief=tk.FLAT,
            padx=10,
            pady=10,
            wrap=tk.WORD
        )
        chat_display.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        for sender, message in self.chat_history:
            timestamp = datetime.now().strftime("%H:%M:%S")
            chat_display.insert(tk.END, f"[{timestamp}] {sender}: {message}\n\n")
        
        chat_display.config(state=tk.DISABLED)
    
    def show_help(self):
        """Show help"""
        if self.jarvis:
            help_text = self.jarvis.get_help_message()
            self.show_response(help_text)
        else:
            messagebox.showinfo("Help", "JARVIS is initializing. Please wait.")
    
    def process_messages(self):
        """Process messages from queue"""
        try:
            while True:
                msg = self.message_queue.get_nowait()
        except queue.Empty:
            pass
        
        self.window.after(100, self.process_messages)
    
    def run(self):
        """Start the GUI"""
        self.window.mainloop()


# Main execution
if __name__ == "__main__":
    print("=" * 50)
    print("Starting JARVIS AI Assistant")
    print("=" * 50)
    
    try:
        API_KEY = "AIzaSyDi1pyCQyCen--a1dkna1iAm8JP1M_-yXA"
        
        print("Creating animated GUI...")
        app = JarvisGUI(API_KEY)
        print("GUI created successfully!")
        print("Starting main loop...")
        app.run()
        print("Application closed")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
