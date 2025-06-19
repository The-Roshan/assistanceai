import speech_recognition as sr
import os
import time
import tkinter as tk
from threading import Thread
import subprocess
import pyautogui

class VoiceAssistant:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Voice Assistant")
        self.root.geometry("400x400")
        self.root.configure(bg="#f0f0f0")
        
        self.is_listening = False
        
        # GUI Elements
        self.title_label = tk.Label(self.root, text="Voice Assistant", font=("Arial", 16, "bold"), bg="#f0f0f0")
        self.title_label.pack(pady=10)
        
        self.status_label = tk.Label(self.root, text="Click 'Start' to begin", font=("Arial", 12), bg="#f0f0f0")
        self.status_label.pack(pady=10)
        
        self.start_button = tk.Button(self.root, text="Start Listening", command=self.start_listening, 
                                    bg="#4CAF50", fg="white")
        self.start_button.pack(pady=10)
        
        self.stop_button = tk.Button(self.root, text="Stop Listening", command=self.stop_listening, 
                                   bg="#f44336", fg="white", state="disabled")
        self.stop_button.pack(pady=10)
        
        self.history_text = tk.Text(self.root, height=12, width=40, state="disabled")
        self.history_text.pack(pady=10)
        
        # App protocol mappings
        self.app_protocols = {
            "whatsapp": "whatsapp:",
            "youtube": "https://www.youtube.com",
            "settings": "ms-settings:"
        }
        
        # Confirmed and common executable fallbacks
        self.app_executables = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "browser": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "chrome": r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
            "paint": "mspaint.exe",
            "file explorer": "explorer.exe",
            "explorer": "explorer.exe",
            "terminal": "cmd.exe",
            "cmd": "cmd.exe",
            "whatsapp": r"C:\Users\{}\AppData\Local\WhatsApp\WhatsApp.exe".format(os.getlogin()),
            "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            "settings": r"C:\Windows\System32\control.exe"
        }
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def log_message(self, message):
        self.history_text.config(state="normal")
        self.history_text.insert(tk.END, message + "\n")
        self.history_text.see(tk.END)
        self.history_text.config(state="disabled")

    def recognize_speech(self):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        try:
            with microphone as source:
                self.log_message("Adjusting for ambient noise... Please wait")
                recognizer.adjust_for_ambient_noise(source, duration=3)  # Increased duration
                self.log_message("Microphone ready - Speak clearly")
                
                while self.is_listening:
                    try:
                        self.status_label.config(text="Listening...", fg="green")
                        audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        self.status_label.config(text="Processing...", fg="orange")
                        
                        command = recognizer.recognize_google(audio, language="en-US").lower()
                        self.log_message(f"Heard: {command}")
                        self.process_command(command)
                        
                    except sr.WaitTimeoutError:
                        self.log_message("No speech detected within 5 seconds")
                        self.status_label.config(text="Listening...", fg="green")
                    except sr.UnknownValueError:
                        self.log_message("Could not understand audio - Try speaking louder or clearer")
                        self.status_label.config(text="Try again", fg="red")
                    except sr.RequestError as e:
                        self.log_message(f"Speech recognition error: {e} - Check internet")
                        self.status_label.config(text="Internet error", fg="red")
                        break
                    except Exception as e:
                        self.log_message(f"Unexpected error: {e}")
                        self.status_label.config(text="Error", fg="red")
                    time.sleep(0.2)  # Slightly increased delay
        except Exception as e:
            self.log_message(f"Microphone error: {e} - Check mic connection")
            self.status_label.config(text="Mic not found", fg="red")
            self.stop_listening()

    def process_command(self, command):
        if "open" in command:
            try:
                app_name = command.split("open", 1)[1].strip()
                if not app_name:
                    self.log_message("No application name specified")
                    self.status_label.config(text="Say app name", fg="blue")
                    return
                
                # Handle "setting" vs "settings"
                if "setting" in app_name:
                    app_name = "settings"
                
                self.launch_application(app_name)
                
            except IndexError:
                self.log_message("Invalid command format")
                self.status_label.config(text="Say 'open [app]'", fg="blue")
        elif "stop" in command or "exit" in command:
            self.stop_listening()

    def launch_application(self, app_name):
        self.log_message(f"Attempting to launch: {app_name}")
        
        # Check protocol first
        for alias, protocol in self.app_protocols.items():
            if alias in app_name:
                try:
                    if protocol.startswith("http"):
                        os.startfile(protocol)
                        self.log_message(f"Launched via URL: {protocol}")
                    else:
                        subprocess.run(f'start "" "{protocol}"', shell=True, check=True)
                        self.log_message(f"Launched via protocol: {protocol}")
                    self.status_label.config(text=f"Opened {app_name}", fg="green")
                    return
                except Exception as e:
                    self.log_message(f"Protocol launch failed: {e}")
                    break
        
        # Fall back to executable paths
        for alias, exe_path in self.app_executables.items():
            if alias in app_name:
                try:
                    if os.path.exists(exe_path):
                        subprocess.Popen(f'"{exe_path}"', shell=True)
                        self.log_message(f"Launched via path: {exe_path}")
                        self.status_label.config(text=f"Opened {app_name}", fg="green")
                        return
                    else:
                        subprocess.Popen(alias, shell=True)
                        self.log_message(f"Launched via PATH: {alias}")
                        self.status_label.config(text=f"Opened {app_name}", fg="green")
                        return
                except Exception as e:
                    self.log_message(f"Executable launch failed: {e}")
        
        # Special case for Settings
        if "settings" in app_name:
            try:
                # Try explorer shell method
                subprocess.Popen(["explorer", "shell:AppsFolder\\Windows.ImmersiveControlPanel_cw5n1h2txyewy!microsoft.windows.immersivecontrolpanel"])
                self.log_message("Launched Settings via Explorer shell")
                self.status_label.config(text="Opened settings", fg="green")
                return
            except Exception as e:
                self.log_message(f"Explorer shell launch failed: {e}")
                try:
                    # Final PowerShell fallback
                    subprocess.Popen(["powershell", "-Command", "Start-Process ms-settings:"])
                    self.log_message("Launched Settings via PowerShell")
                    self.status_label.config(text="Opened settings", fg="green")
                    return
                except Exception as e:
                    self.log_message(f"PowerShell launch failed: {e}")
        
        self.log_message(f"All attempts failed for {app_name}")
        self.status_label.config(text="App not found", fg="red")

    def start_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_label.config(text="Initializing...", fg="blue")
            
            self.listen_thread = Thread(target=self.recognize_speech)
            self.listen_thread.daemon = True
            self.listen_thread.start()

    def stop_listening(self):
        if self.is_listening:
            self.is_listening = False
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.status_label.config(text="Stopped", fg="black")

    def on_closing(self):
        self.is_listening = False
        if hasattr(self, 'listen_thread'):
            self.listen_thread.join(timeout=1.0)
        self.root.destroy()

if __name__ == "__main__":
    try:
        import speech_recognition
        import pyautogui
        VoiceAssistant()
    except ImportError:
        print("Please install required libraries:")
        print("pip install SpeechRecognition PyAudio pyautogui")