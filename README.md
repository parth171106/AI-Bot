AI-Chatbot
========

This is a virtual assistant application that integrates speech recognition, text-to-speech, real-time search, automation, and a graphical user interface (GUI). It is designed to interact with users, perform tasks, and provide intelligent responses based on user queries.

---

Features
--------
- Speech Recognition: Converts user speech into text for processing.
- Text-to-Speech: Converts text responses into speech for user interaction.
- Real-Time Search: Performs real-time searches using Google and Groq APIs.
- Automation: Handles tasks like opening/closing apps, performing searches, and more.
- Image Generation: Generates images based on prompts using the Hugging Face API.
- GUI: A user-friendly graphical interface built with PyQt5.
- Chatbot: Conversational AI for general queries.

---

Project Structure
-----------------
AI-Chatbot/
├── Backend/
│   ├── Automation.py          # Handles automation tasks
│   ├── Chatbot.py             # Conversational AI chatbot
│   ├── ImageGenereation.py    # Image generation using Hugging Face API
│   ├── Model.py               # Decision-making model for query classification
│   ├── RealtimeSearchEngine.py # Real-time search functionality
│   ├── SpeechToText.py        # Converts speech to text
│   ├── TextToSpeech.py        # Converts text to speech
│   └── __pycache__/           # Compiled Python files
│
├── Frontend/
│   ├── GUI.py                 # GUI implementation using PyQt5
│   ├── Files/                 # Temporary data files
│   ├── Graphics/              # Graphical assets (icons, animations, etc.)
│   └── __pycache__/           # Compiled Python files
│
├── Data/
│   ├── ChatLog.json           # Stores chat history
│   ├── Voice.html             # HTML file for speech recognition
│   └── speech.mp3             # Temporary file for generated speech
│
├── venv/                      # Virtual environment (excluded from Git)
├── Main.py                    # Entry point of the application
├── .env                       # Environment variables (excluded from Git)
├── Requirements.txt           # Python dependencies
└── README.txt                 # Project documentation

---

Installation
------------
1. Clone the repository:
   git clone https://github.com/parth171106/AI-Bot.git
   cd AI-Chatbot

2. Create and activate a virtual environment:
   python -m venv venv
   venv\Scripts\activate  # On Windows

3. Install dependencies:
   pip install -r Requirements.txt

4. Set up environment variables:
   - Create a `.env` file in the root directory.
   - Add the following:
     API_KEY=your_api_key
     ASSISTANT_NAME=YourPreferredName
     USER_NAME=YourName

---

Usage
-----
1. Run the application:
   python Main.py

2. Interact with the assistant via the GUI:
   - Use the microphone to give voice commands.
   - View responses in the chat window.

---

Technologies Used
-----------------
- Python: Core programming language.
- PyQt5: For building the graphical user interface.
- edge-tts: For text-to-speech conversion.
- Hugging Face API: For image generation.
- Groq API: For chatbot and real-time search functionality.

---

Future Improvements
-------------------
- Enhance error handling for better user experience.
- Optimize the decision-making model for faster query classification.
- Add more automation tasks and integrations.
- Improve documentation and testing.


---

Contributing
------------
Contributions are welcome! Feel free to fork the repository and submit a pull request.

---

Contact
-------
For any inquiries or issues, please contact:
- Name: Parth Khunt
- Email: alpha.parth009@gmail.com
