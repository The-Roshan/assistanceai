import speech_recognition as sr
import os
import time
import tkinter as tk
from threading import Thread
import subprocess
import pyautogui
import google.generativeai as genai
from datetime import datetime, timedelta
import webbrowser
import getpass
import smtplib
from email.mime.text import MIMEText
from gtts import gTTS
import pygame
import glob
import re
import psutil
import screen_brightness_control as sbc
from googletrans import Translator
import requests

class VoiceAssistant:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Tasa - Ultimate Voice Assistant")
        self.root.geometry("600x700")
        self.root.configure(bg="#f0f0f0")
        
        self.is_listening = False
        self.is_active = False
        self.is_responding = False
        self.is_playing_music = False
        self.alarms = []
        self.timers = []
        
        # Initialize pygame for audio playback
        pygame.mixer.init()
        
        # Create history_text first
        self.history_text = tk.Text(self.root, height=15, width=60, state="disabled")
        self.history_text.pack(pady=10)
        
        # Configure Gemini API
        self.api_key = "AIzaSyBPgU1268WDf2r0-nFMOxiRI-eWYIMXekQ"
        genai.configure(api_key=self.api_key)
        
        # Initialize Gemini model
        self.gemini_model = None
        try:
            models = genai.list_models()
            self.log_message("Available models:")
            for model in models:
                if "generateContent" in model.supported_generation_methods:
                    self.log_message(f"Model: {model.name}")
            model_name = "gemini-1.5-flash"
            self.log_message(f"Attempting to use model: {model_name}")
            self.gemini_model = genai.GenerativeModel(model_name)
            self.log_message(f"Successfully initialized model: {model_name}")
        except Exception as e:
            self.log_message(f"Error initializing Gemini model: {e}")
        
        # GUI Elements
        self.title_label = tk.Label(self.root, text="Tasa - Ultimate Assistant", font=("Arial", 16, "bold"), bg="#f0f0f0")
        self.title_label.pack(pady=10)
        
        self.time_label = tk.Label(self.root, text="", font=("Arial", 12), bg="#f0f0f0")
        self.time_label.pack(pady=5)
        self.update_time()
        
        self.status_label = tk.Label(self.root, text="Click 'Start' to begin", font=("Arial", 12), bg="#f0f0f0")
        self.status_label.pack(pady=10)
        
        # Volume Control
        self.volume_label = tk.Label(self.root, text="Speech Volume", font=("Arial", 10), bg="#f0f0f0")
        self.volume_label.pack(pady=5)
        self.volume_scale = tk.Scale(self.root, from_=0, to=100, orient=tk.HORIZONTAL, bg="#f0f0f0", length=200)
        self.volume_scale.set(50)  # Default volume
        self.volume_scale.pack(pady=5)
        
        # Button Frame
        self.button_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.button_frame.pack(pady=10)
        
        self.start_button = tk.Button(self.button_frame, text="Start Listening", command=self.start_listening, 
                                    bg="#4CAF50", fg="white")
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = tk.Button(self.button_frame, text="Stop Listening", command=self.stop_listening, 
                                   bg="#f44336", fg="white", state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_respond_button = tk.Button(self.button_frame, text="Stop Respond", command=self.stop_respond, 
                                           bg="#FF9800", fg="white", state="disabled")
        self.stop_respond_button.pack(side=tk.LEFT, padx=5)
        
        self.screenshot_button = tk.Button(self.button_frame, text="Take Screenshot", command=self.take_screenshot, 
                                         bg="#2196F3", fg="white")
        self.screenshot_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_log_button = tk.Button(self.button_frame, text="Clear Log", command=self.clear_log, 
                                        bg="#9C27B0", fg="white")
        self.clear_log_button.pack(side=tk.LEFT, padx=5)
        
        # App protocol mappings
        self.app_protocols = {
            "whatsapp": "whatsapp:",
            "youtube": "https://www.youtube.com",
            "settings": "ms-settings:"
        }
        
        # Executable fallbacks
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
        
        # Website mappings
        self.websites = {
            "google": "https://www.google.com",
            "wikipedia": "https://www.wikipedia.org",
            "reddit": "https://www.reddit.com",
            "twitter": "https://www.twitter.com",
            "facebook": "https://www.facebook.com"
        }
        
        # Start alarm and timer checking threads
        self.alarm_thread = Thread(target=self.check_alarms, daemon=True)
        self.alarm_thread.start()
        self.timer_thread = Thread(target=self.check_timers, daemon=True)
        self.timer_thread.start()
        
        # Initialize translator
        self.translator = Translator()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def log_message(self, message):
        try:
            if hasattr(self, 'history_text') and self.history_text.winfo_exists():
                self.history_text.config(state="normal")
                self.history_text.insert(tk.END, message + "\n")
                self.history_text.see(tk.END)
                self.history_text.config(state="disabled")
            else:
                print(f"Log (GUI unavailable): {message}")
        except tk.TclError:
            print(f"Log (GUI destroyed): {message}")

    def clear_log(self):
        self.history_text.config(state="normal")
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state="disabled")
        self.log_message("Log cleared")

    def speak(self, text):
        if not self.is_responding:
            self.is_responding = True
            self.stop_respond_button.config(state="normal")
            self.log_message(f"Speaking: {text}")
            try:
                # Generate speech with gTTS
                tts = gTTS(text=text, lang='en')
                temp_file = "temp_speech.mp3"
                tts.save(temp_file)
                
                # Play the speech with pygame on a specific channel
                speech_channel = pygame.mixer.Channel(2)
                speech_channel.set_volume(self.volume_scale.get() / 100.0)
                speech_channel.play(pygame.mixer.Sound(temp_file))
                while speech_channel.get_busy():
                    pygame.time.Clock().tick(10)
                
                # Clean up
                os.remove(temp_file)
            except Exception as e:
                self.log_message(f"Speech error: {e}")
            finally:
                self.is_responding = False
                self.stop_respond_button.config(state="disabled")

    def stop_respond(self):
        if self.is_responding:
            self.log_message("Stopping current response")
            pygame.mixer.Channel(2).stop()
            self.is_responding = False
            self.is_active = False
            self.stop_respond_button.config(state="disabled")
            self.status_label.config(text="Waiting for 'Hey Tasa'...", fg="blue")
            self.speak("Response stopped, say Hey Tasa to continue")

    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S %Y-%m-%d")
        self.time_label.config(text=f"Current Time: {current_time}")
        self.root.after(1000, self.update_time)

    def recognize_speech(self):
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        try:
            with microphone as source:
                self.log_message("Adjusting for ambient noise... Please wait")
                self.speak("Adjusting microphone, please wait")
                recognizer.adjust_for_ambient_noise(source, duration=3)
                self.log_message("Microphone ready - Say 'Hey Tasa' to activate")
                self.speak("Microphone ready, say Hey Tasa to activate")
                
                while self.is_listening:
                    try:
                        self.status_label.config(text="Waiting for 'Hey Tasa'...", fg="blue")
                        audio = recognizer.listen(source, timeout=None, phrase_time_limit=5)
                        command = recognizer.recognize_google(audio, language="en-US").lower()
                        self.log_message(f"Heard: {command}")
                        
                        if "hey tasa" in command:
                            self.is_active = True
                            self.status_label.config(text="Listening...", fg="green")
                            self.speak("Yes, how can I assist you?")
                            self.process_command(command.replace("hey tasa", "").strip())
                            while self.is_active and self.is_listening:
                                try:
                                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                                    follow_up = recognizer.recognize_google(audio, language="en-US").lower()
                                    self.log_message(f"Heard: {follow_up}")
                                    self.process_command(follow_up)
                                except sr.WaitTimeoutError:
                                    self.log_message("No follow-up detected, deactivating")
                                    self.speak("No response, going back to waiting")
                                    self.is_active = False
                                    break
                                except sr.UnknownValueError:
                                    self.speak("Could not understand, please try again")
                        elif self.is_active:
                            self.process_command(command)
                            
                    except sr.UnknownValueError:
                        if not self.is_active:
                            self.log_message("Could not understand audio - Say 'Hey Tasa'")
                        self.status_label.config(text="Waiting for 'Hey Tasa'...", fg="blue")
                    except sr.RequestError as e:
                        self.log_message(f"Speech recognition error: {e}")
                        self.speak("Internet error, please check your connection")
                        self.status_label.config(text="Internet error", fg="red")
                        break
                    except Exception as e:
                        self.log_message(f"Unexpected error: {e}")
                        self.speak("An error occurred")
                        self.status_label.config(text="Error", fg="red")
                    time.sleep(0.2)
        except Exception as e:
            self.log_message(f"Microphone error: {e}")
            self.speak("Microphone not found")
            self.status_label.config(text="Mic not found", fg="red")
            self.stop_listening()

    def process_command(self, command):
        if not command:
            return
        
        if self.is_responding:
            self.log_message("Processing interrupted by new command")
            pygame.mixer.Channel(2).stop()
            self.is_responding = False
        
        # App Opening
        if "open" in command:
            try:
                app_name = command.split("open", 1)[1].strip()
                if not app_name:
                    self.log_message("No application name specified")
                    self.speak("Please say an application name")
                    self.status_label.config(text="Say app name", fg="blue")
                    return
                
                if "setting" in app_name:
                    app_name = "settings"
                self.launch_application(app_name)
                
            except IndexError:
                self.log_message("Invalid command format")
                self.speak("Please say 'open' followed by an app name")
                self.status_label.config(text="Say 'open [app]'", fg="blue")
        
        # System Commands
        elif "shutdown" in command:
            self.log_message("Initiating shutdown")
            self.speak("Shutting down the computer in 30 seconds. Say cancel to stop.")
            subprocess.Popen("shutdown /s /t 30", shell=True)
        
        elif "cancel shutdown" in command or "cancel" in command:
            self.log_message("Cancelling shutdown")
            self.speak("Shutdown cancelled")
            subprocess.Popen("shutdown /a", shell=True)
        
        elif "restart" in command:
            self.log_message("Initiating restart")
            self.speak("Restarting the computer in 30 seconds. Say cancel to stop.")
            subprocess.Popen("shutdown /r /t 30", shell=True)
        
        elif "sleep" in command:
            self.log_message("Putting computer to sleep")
            self.speak("Going to sleep")
            subprocess.Popen("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        
        elif "mute" in command:
            self.log_message("Muting volume")
            self.speak("Volume muted")
            pyautogui.press("volumemute")
        
        elif "volume up" in command:
            self.log_message("Increasing volume")
            self.speak("Volume increased")
            pyautogui.press("volumeup")
            pyautogui.press("volumeup")
        
        elif "volume down" in command:
            self.log_message("Decreasing volume")
            self.speak("Volume decreased")
            pyautogui.press("volumedown")
            pyautogui.press("volumedown")
        
        # Brightness Control
        elif "increase brightness" in command:
            self.adjust_brightness(increase=True)
        
        elif "decrease brightness" in command:
            self.adjust_brightness(increase=False)
        
        # File Operations
        elif "create file" in command:
            self.create_text_file()
        
        elif "open file" in command or "open folder" in command:
            self.open_file_or_folder(command)
        
        # Take Note
        elif "take a note" in command:
            self.take_note(command)
        
        # Web Search
        elif "search" in command:
            query = command.replace("search", "").strip()
            if query:
                self.web_search(query)
            else:
                self.speak("Please specify what to search for")
        
        # Open Website
        elif "open website" in command:
            self.open_website(command)
        
        # Time and Date
        elif "time" in command:
            current_time = datetime.now().strftime("%I:%M %p")
            self.log_message(f"Current time: {current_time}")
            self.speak(f"The time is {current_time}")
        
        elif "date" in command:
            current_date = datetime.now().strftime("%B %d, %Y")
            self.log_message(f"Current date: {current_date}")
            self.speak(f"Today is {current_date}")
        
        # Weather (via Gemini)
        elif "weather" in command:
            location = command.replace("weather", "").replace("in", "").strip()
            if not location:
                location = "current location"
            self.get_weather(location)
        
        # Screenshot
        elif "screenshot" in command:
            self.take_screenshot()
        
        # Play Music
        elif "play music" in command:
            self.play_music()
        
        # Stop Music
        elif "stop music" in command:
            self.stop_music()
        
        # Set Alarm
        elif "set alarm" in command:
            self.set_alarm(command)
        
        # Set Timer
        elif "set timer" in command:
            self.set_timer(command)
        
        # Send Email
        elif "send email" in command:
            self.send_email(command)
        
        # Read Notifications
        elif "read notifications" in command:
            self.read_notifications()
        
        # Check Battery
        elif "check battery" in command:
            self.check_battery()
        
        # Tell a Joke
        elif "tell a joke" in command:
            self.tell_joke()
        
        # Translate
        elif "translate" in command:
            self.translate_text(command)
        
        # Stop Command
        elif "stop" in command or "exit" in command:
            self.speak("Stopping the assistant")
            self.stop_listening()
        
        # Gemini for General Questions
        else:
            self.log_message(f"Question detected: {command}")
            response = self.ask_gemini(command)
            self.log_message(f"Response: {response}")
            self.speak(response)

    def ask_gemini(self, question):
        if not self.gemini_model:
            return "Gemini model not initialized. Please check the logs for available models."
        if not self.is_responding:
            try:
                response = self.gemini_model.generate_content(question)
                return response.text
            except Exception as e:
                self.log_message(f"Gemini API error: {e}")
                return "Sorry, I couldn't process that question right now. Please try again."
        return "Response interrupted"

    def launch_application(self, app_name):
        self.log_message(f"Attempting to launch: {app_name}")
        self.speak(f"Opening {app_name}")
        
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
        
        if "settings" in app_name:
            try:
                subprocess.Popen(["explorer", "shell:AppsFolder\\Windows.ImmersiveControlPanel_cw5n1h2txyewy!microsoft.windows.immersivecontrolpanel"])
                self.log_message("Launched Settings via Explorer shell")
                self.status_label.config(text="Opened settings", fg="green")
                return
            except Exception as e:
                self.log_message(f"Explorer shell launch failed: {e}")
                try:
                    subprocess.Popen(["powershell", "-Command", "Start-Process ms-settings:"])
                    self.log_message("Launched Settings via PowerShell")
                    self.status_label.config(text="Opened settings", fg="green")
                    return
                except Exception as e:
                    self.log_message(f"PowerShell launch failed: {e}")
        
        self.log_message(f"All attempts failed for {app_name}")
        self.speak(f"Could not find {app_name}")
        self.status_label.config(text="App not found", fg="red")

    def create_text_file(self):
        try:
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            filename = f"new_file_{int(time.time())}.txt"
            filepath = os.path.join(desktop, filename)
            with open(filepath, 'w') as f:
                f.write("Created by Tasa Voice Assistant")
            self.log_message(f"Created file: {filepath}")
            self.speak(f"Created a new text file on your desktop named {filename}")
        except Exception as e:
            self.log_message(f"Error creating file: {e}")
            self.speak("Sorry, I couldn't create the file")

    def open_file_or_folder(self, command):
        try:
            target = command.replace("open file", "").replace("open folder", "").strip()
            if not target:
                self.speak("Please specify a file or folder name")
                return
            
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            target_path = os.path.join(desktop, target)
            if os.path.exists(target_path):
                os.startfile(target_path)
                self.log_message(f"Opened: {target_path}")
                self.speak(f"Opened {target}")
            else:
                self.log_message(f"File/Folder not found on Desktop: {target}")
                self.speak(f"Could not find {target} on your desktop")
        except Exception as e:
            self.log_message(f"Error opening file/folder: {e}")
            self.speak("Sorry, I couldn't open that file or folder")

    def web_search(self, query):
        try:
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            self.log_message(f"Searching Google for: {query}")
            self.speak(f"Searching Google for {query}")
        except Exception as e:
            self.log_message(f"Error performing web search: {e}")
            self.speak("Sorry, I couldn't perform the search")

    def open_website(self, command):
        try:
            website_name = command.replace("open website", "").strip()
            if website_name in self.websites:
                url = self.websites[website_name]
                webbrowser.open(url)
                self.log_message(f"Opening website: {website_name}")
                self.speak(f"Opening {website_name}")
            else:
                self.speak(f"Sorry, I don't know the website {website_name}. Try google, wikipedia, or reddit.")
        except Exception as e:
            self.log_message(f"Error opening website: {e}")
            self.speak("Sorry, I couldn't open the website")

    def get_weather(self, location):
        try:
            weather_query = f"What is the weather in {location} today?"
            response = self.ask_gemini(weather_query)
            self.log_message(f"Weather query: {weather_query}")
            self.log_message(f"Weather response: {response}")
            self.speak(response)
        except Exception as e:
            self.log_message(f"Error getting weather: {e}")
            self.speak("Sorry, I couldn't get the weather information")

    def take_screenshot(self):
        try:
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            filename = f"screenshot_{int(time.time())}.png"
            filepath = os.path.join(desktop, filename)
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath)
            self.log_message(f"Screenshot saved: {filepath}")
            self.speak(f"Screenshot saved to your desktop as {filename}")
        except Exception as e:
            self.log_message(f"Error taking screenshot: {e}")
            self.speak("Sorry, I couldn't take a screenshot")

    def play_music(self):
        if self.is_playing_music:
            self.speak("Music is already playing")
            return
        
        self.is_playing_music = True
        music_dir = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Music')
        music_files = glob.glob(os.path.join(music_dir, "*.mp3"))
        
        if not music_files:
            self.log_message("No music files found in Music directory")
            self.speak("No music files found in your Music directory")
            self.is_playing_music = False
            return
        
        self.log_message("Playing music")
        self.speak("Playing music")
        
        # Use a separate channel for music
        self.music_channel = pygame.mixer.Channel(0)
        
        def play_music_thread():
            for music_file in music_files:
                if not self.is_playing_music:
                    break
                try:
                    self.music_channel.play(pygame.mixer.Sound(music_file))
                    while self.music_channel.get_busy() and self.is_playing_music:
                        pygame.time.Clock().tick(10)
                except Exception as e:
                    self.log_message(f"Error playing music: {e}")
                    self.speak("Error playing music")
            self.is_playing_music = False
        
        self.music_thread = Thread(target=play_music_thread, daemon=True)
        self.music_thread.start()

    def stop_music(self):
        if self.is_playing_music:
            self.is_playing_music = False
            self.music_channel.stop()
            self.log_message("Music stopped")
            self.speak("Music stopped")
        else:
            self.speak("No music is playing")

    def set_alarm(self, command):
        try:
            time_str = command.replace("set alarm for", "").strip()
            minutes = int(re.search(r'\d+', time_str).group())
            alarm_time = datetime.now() + timedelta(minutes=minutes)
            self.alarms.append(alarm_time)
            self.log_message(f"Alarm set for {alarm_time.strftime('%H:%M:%S')}")
            self.speak(f"Alarm set for {minutes} minutes from now")
        except Exception as e:
            self.log_message(f"Error setting alarm: {e}")
            self.speak("Sorry, I couldn't set the alarm. Please say the time in minutes, like set alarm for 5 minutes.")

    def check_alarms(self):
        while True:
            current_time = datetime.now()
            for alarm in self.alarms[:]:
                if current_time >= alarm:
                    alarm_channel = pygame.mixer.Channel(1)
                    tts = gTTS(text="Alarm! Time to wake up!", lang='en')
                    temp_file = "alarm.mp3"
                    tts.save(temp_file)
                    alarm_channel.play(pygame.mixer.Sound(temp_file))
                    while alarm_channel.get_busy():
                        pygame.time.Clock().tick(10)
                    os.remove(temp_file)
                    self.alarms.remove(alarm)
            time.sleep(1)

    def set_timer(self, command):
        try:
            time_str = command.replace("set timer for", "").strip()
            minutes = int(re.search(r'\d+', time_str).group())
            timer_end = datetime.now() + timedelta(minutes=minutes)
            self.timers.append((timer_end, minutes))
            self.log_message(f"Timer set for {timer_end.strftime('%H:%M:%S')}")
            self.speak(f"Timer set for {minutes} minutes")
        except Exception as e:
            self.log_message(f"Error setting timer: {e}")
            self.speak("Sorry, I couldn't set the timer. Please say the time in minutes, like set timer for 5 minutes.")

    def check_timers(self):
        while True:
            current_time = datetime.now()
            for timer in self.timers[:]:
                end_time, minutes = timer
                if current_time >= end_time:
                    alarm_channel = pygame.mixer.Channel(1)
                    tts = gTTS(text=f"Timer for {minutes} minutes is up!", lang='en')
                    temp_file = "timer.mp3"
                    tts.save(temp_file)
                    alarm_channel.play(pygame.mixer.Sound(temp_file))
                    while alarm_channel.get_busy():
                        pygame.time.Clock().tick(10)
                    os.remove(temp_file)
                    self.timers.remove(timer)
            time.sleep(1)

    def send_email(self, command):
        try:
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', command)
            if not email_match:
                self.speak("Please specify a valid email address, like test@example.com")
                return
            recipient = email_match.group()
            
            sender_email = "your_email@gmail.com"  # Replace with your email
            sender_password = "your_app_password"  # Replace with your App Password
            subject = "Message from Tasa Voice Assistant"
            body = "This is a test email sent by Tasa Voice Assistant."
            
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = sender_email
            msg['To'] = recipient
            
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, recipient, msg.as_string())
            
            self.log_message(f"Email sent to {recipient}")
            self.speak(f"Email sent to {recipient}")
        except Exception as e:
            self.log_message(f"Error sending email: {e}")
            self.speak("Sorry, I couldn't send the email. Please check your email configuration or the recipient address.")

    def read_notifications(self):
        notifications = [
            "You have a new email from John",
            "Meeting reminder at 3 PM",
            "Missed call from Sarah"
        ]
        if not notifications:
            self.speak("No new notifications")
        else:
            self.speak("Here are your notifications")
            for notif in notifications:
                self.speak(notif)
                pygame.time.Clock().tick(10)

    def adjust_brightness(self, increase=True):
        try:
            current_brightness = sbc.get_brightness()[0]
            if increase:
                new_brightness = min(100, current_brightness + 10)
                sbc.set_brightness(new_brightness)
                self.speak("Brightness increased")
            else:
                new_brightness = max(0, current_brightness - 10)
                sbc.set_brightness(new_brightness)
                self.speak("Brightness decreased")
            self.log_message(f"Brightness set to {new_brightness}%")
        except Exception as e:
            self.log_message(f"Error adjusting brightness: {e}")
            self.speak("Sorry, I couldn't adjust the brightness")

    def take_note(self, command):
        try:
            note_content = command.replace("take a note", "").strip()
            if not note_content:
                self.speak("Please specify the note content")
                return
            desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            filename = f"note_{int(time.time())}.txt"
            filepath = os.path.join(desktop, filename)
            with open(filepath, 'w') as f:
                f.write(note_content)
            self.log_message(f"Note saved: {filepath}")
            self.speak(f"Note saved to your desktop as {filename}")
        except Exception as e:
            self.log_message(f"Error taking note: {e}")
            self.speak("Sorry, I couldn't save the note")

    def check_battery(self):
        try:
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                plugged = "plugged in" if battery.power_plugged else "not plugged in"
                self.log_message(f"Battery: {percent}% ({plugged})")
                self.speak(f"Battery is at {percent} percent and is {plugged}")
            else:
                self.speak("Battery information not available")
        except Exception as e:
            self.log_message(f"Error checking battery: {e}")
            self.speak("Sorry, I couldn't check the battery status")

    def tell_joke(self):
        try:
            # Hardcoded jokes for simplicity
            jokes = [
                "Why did the scarecrow become a motivational speaker? Because he was outstanding in his field!",
                "What do you call fake spaghetti? An impasta!",
                "Why don't skeletons fight in school? They don't have the guts for it!"
            ]
            import random
            joke = random.choice(jokes)
            self.log_message(f"Joke: {joke}")
            self.speak(joke)
        except Exception as e:
            self.log_message(f"Error telling joke: {e}")
            self.speak("Sorry, I couldn't tell a joke right now")

    def translate_text(self, command):
        try:
            # Extract text and language (e.g., "translate hello to Spanish")
            parts = command.replace("translate", "").split("to")
            if len(parts) != 2:
                self.speak("Please say translate [text] to [language], like translate hello to Spanish")
                return
            text = parts[0].strip()
            language = parts[1].strip().lower()
            
            # Map language to code
            lang_codes = {
                "spanish": "es",
                "french": "fr",
                "german": "de",
                "italian": "it",
                "japanese": "ja",
                "chinese": "zh-cn"
            }
            if language not in lang_codes:
                self.speak(f"Sorry, I don't support {language}. Try Spanish, French, German, Italian, Japanese, or Chinese.")
                return
            
            translated = self.translator.translate(text, dest=lang_codes[language])
            self.log_message(f"Translated '{text}' to {language}: {translated.text}")
            self.speak(f"The translation of {text} to {language} is {translated.text}")
        except Exception as e:
            self.log_message(f"Error translating text: {e}")
            self.speak("Sorry, I couldn't translate the text")

    def start_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.status_label.config(text="Initializing...", fg="blue")
            self.speak("Tasa is starting")
            
            self.listen_thread = Thread(target=self.recognize_speech)
            self.listen_thread.daemon = True
            self.listen_thread.start()

    def stop_listening(self):
        if self.is_listening:
            self.is_listening = False
            self.is_active = False
            self.is_responding = False
            pygame.mixer.Channel(2).stop()
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.stop_respond_button.config(state="disabled")
            self.status_label.config(text="Stopped", fg="black")
            self.log_message("Tasa stopped")
            self.speak("Listening stopped")

    def on_closing(self):
        self.is_listening = False
        self.is_active = False
        self.is_responding = False
        self.is_playing_music = False
        pygame.mixer.quit()
        self.speak("Tasa is shutting down")
        if hasattr(self, 'listen_thread'):
            self.listen_thread.join(timeout=1.0)
        self.root.destroy()

if __name__ == "__main__":
    try:
        import speech_recognition
        import pyautogui
        import google.generativeai
        import pygame
        import gtts
        import psutil
        import screen_brightness_control
        import googletrans
        import requests
        VoiceAssistant()
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please install required libraries:")
        print("pip install SpeechRecognition PyAudio pyautogui google-generativeai pygame gTTS psutil screen-brightness-control googletrans requests")
    except Exception as e:
        print(f"Unexpected error: {e}")