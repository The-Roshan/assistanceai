# Tasa - Ultimate Voice Assistant

## Overview

Tasa is a sophisticated, voice-activated personal assistant designed to enhance productivity and user interaction through natural language processing. Built with Python, Tasa leverages advanced speech recognition, text-to-speech synthesis, and integration with Google's Gemini AI model to provide a seamless and interactive experience. It supports a wide range of functionalities, including application launching, system control, web searching, email sending, and more, all accessible via a user-friendly GUI.

## Features

- **Voice Activation**: Activate Tasa with the wake phrase "Hey Tasa" and issue follow-up commands naturally.
- **Application Control**: Open applications using voice commands, supporting both protocol-based (e.g., WhatsApp, YouTube) and executable-based launches (e.g., Notepad, Chrome).
- **System Commands**: Perform system operations such as shutdown, restart, sleep, volume control, and screen brightness adjustment.
- **File Operations**: Create text files, open files or folders on the desktop, and take notes via voice input.
- **Web Integration**: Conduct Google searches, open predefined websites (e.g., Google, Wikipedia), and retrieve weather information using the Gemini AI model.
- **Multimedia**: Play and stop music from the user's Music directory using pygame.
- **Time Management**: Set alarms and timers with voice commands, with notifications via text-to-speech.
- **Email Sending**: Send emails using a configured Gmail account (requires user setup for sender credentials).
- **System Monitoring**: Check battery status and read mock notifications.
- **Humor and Language**: Tell jokes and translate text into supported languages (e.g., Spanish, French, Japanese).
- **GUI Interface**: A Tkinter-based interface displays command history, current time, and system status, with controls for starting/stopping listening, taking screenshots, and adjusting speech volume.

## Prerequisites

To run Tasa, ensure the following dependencies are installed:

- Python 3.7 or higher
- Required Python libraries:
  ```bash
  pip install SpeechRecognition PyAudio pyautogui google-generativeai pygame gTTS psutil screen-brightness-control googletrans==3.1.0a0 requests
  ```

Additionally, you need:
- A valid Google Gemini API key (replace the placeholder in the code with your own key).
- A working microphone for speech recognition.
- A Gmail account with an App Password for email functionality (configure sender email and password in the `send_email` method).
- Internet connectivity for web searches, weather queries, and translation.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd tasa-voice-assistant
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   Create a `requirements.txt` file with:
   ```
   SpeechRecognition
   PyAudio
   pyautogui
   google-generativeai
   pygame
   gTTS
   psutil
   screen-brightness-control
   googletrans==3.1.0a0
   requests
   ```

3. **Configure API Key**:
   - Obtain a Google Gemini API key from [Google's API Console](https://console.cloud.google.com/).
   - Replace the placeholder `self.api_key = "AIzaSyBPgU1268WDf2r0-nFMOxiRI-eWYIMXekQ"` in the code with your API key.

4. **Configure Email Settings** (Optional):
   - Update the `send_email` method with your Gmail address and App Password.
   - Generate an App Password from your Google Account settings if 2-factor authentication is enabled.

5. **Run the Application**:
   ```bash
   python tasa.py
   ```

## Usage

1. **Launch Tasa**:
   - Run the script to open the Tkinter GUI.
   - Click the "Start Listening" button or say "Hey Tasa" to activate voice recognition.

2. **Voice Commands**:
   - **Wake Command**: "Hey Tasa" to activate the assistant.
   - **Application Launch**: "Open [app_name]" (e.g., "Open Notepad", "Open Chrome", "Open WhatsApp").
   - **System Control**:
     - "Shutdown" / "Cancel shutdown"
     - "Restart"
     - "Sleep"
     - "Mute" / "Volume up" / "Volume down"
     - "Increase brightness" / "Decrease brightness"
   - **File Operations**:
     - "Create file"
     - "Open file [name]" / "Open folder [name]"
     - "Take a note [content]"
   - **Web and Search**:
     - "Search [query]" (e.g., "Search Python tutorials")
     - "Open website [name]" (e.g., "Open website Google")
     - "Weather in [location]" (e.g., "Weather in New York")
   - **Multimedia**:
     - "Play music"
     - "Stop music"
   - **Time Management**:
     - "Set alarm for [minutes] minutes" (e.g., "Set alarm for 10 minutes")
     - "Set timer for [minutes] minutes" (e.g., "Set timer for 5 minutes")
   - **Email**:
     - "Send email to [email_address]" (e.g., "Send email to test@example.com")
   - **System Monitoring**:
     - "Check battery"
     - "Read notifications"
   - **Miscellaneous**:
     - "Tell a joke"
     - "Translate [text] to [language]" (e.g., "Translate hello to Spanish")
     - "Time" / "Date"
     - "Stop" / "Exit" to stop listening

3. **GUI Controls**:
   - **Start Listening**: Begins voice recognition.
   - **Stop Listening**: Halts voice recognition.
   - **Stop Respond**: Interrupts current speech output.
   - **Take Screenshot**: Captures and saves a screenshot to the desktop.
   - **Clear Log**: Clears the command history in the GUI.
   - **Volume Slider**: Adjusts the speech output volume.

4. **Stopping Tasa**:
   - Click the "Stop Listening" button or say "Stop" / "Exit".
   - Close the GUI window to terminate the application.

## Project Structure

```
tasa-voice-assistant/
├── tasa.py                # Main script containing the VoiceAssistant class
├── requirements.txt       # List of required Python libraries
└── README.md             # This file
```

## Notes

- **Platform Compatibility**: Tasa is designed for Windows due to specific system commands (e.g., `shutdown`, `ms-settings:`). Modifications are needed for macOS or Linux support.
- **Gemini API**: Requires a valid API key and internet connection. Ensure the `gemini-1.5-flash` model is available in your region.
- **Email Setup**: The `send_email` method requires a Gmail account with an App Password. Replace placeholder credentials before use.
- **Music Playback**: Only plays `.mp3` files from the user's Music directory. Ensure files are present for the "Play music" command.
- **Error Handling**: Tasa logs errors to the GUI and console, ensuring robust operation even if certain features fail.
- **Security**: Store sensitive information (API key, email credentials) securely, ideally using environment variables or a configuration file.

## Limitations

- **Speech Recognition**: Requires a good-quality microphone and quiet environment for optimal performance.
- **Internet Dependency**: Features like web search, weather, and translation require an active internet connection.
- **Application Paths**: Some application paths (e.g., WhatsApp, Chrome) are hardcoded and may need adjustment based on your system.
- **Language Support**: Translation is limited to a predefined set of languages. Additional languages can be added by extending the `lang_codes` dictionary.
- **Notifications**: Currently uses mock notifications. Integration with real notification systems requires additional development.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make changes and commit (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

Please ensure code follows PEP 8 style guidelines and includes appropriate error handling.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with Python and libraries including SpeechRecognition, gTTS, pygame, and google-generativeai.
- Powered by Google's Gemini AI for natural language processing.
- Inspired by modern voice assistants like Siri and Alexa.

## Contact

For issues, suggestions, or questions, please open an issue on the GitHub repository or contact the maintainer at [your-email@example.com].

---
*Last updated: June 19, 2025*