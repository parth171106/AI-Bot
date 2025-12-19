# Import required libraries
from AppOpener import close, open as appopen  # Open and close apps
from webbrowser import open as webopen        # Open URLs in the default browser
from pywhatkit import search, playonyt         # Search online and play YouTube content
from dotenv import dotenv_values               # Load environment variables from .env
from bs4 import BeautifulSoup                  # Parse HTML content
from rich import print
from groq import Groq                          # Interact with Groq API
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os

# Load API key from .env
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
Username = env_vars.get("Username")

# HTML parsing class targets
classes = [
    "zCubwf", "hgKELc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSB YwPhnf",
    "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "O5uR6d LTKOO",
    "vlzY6d", "webanswers-webanswers_table__webanswers-table",
    "dDoNo ikb4Bb gsrt", "sXLaOe", "LWkfKe", "VQF4g", "qv3Wpe",
    "kno-rdesc", "SPZz6b"
]

# User-agent for simulating a browser request
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

# Initialize Groq client
client = Groq(api_key=GroqAPIKey)

# Professional-sounding default responses
professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
    "I'm at your service for any additional questions or support you may need—don't hesitate to ask.",
]

# Message log and system prompt
messages = []

SystemChatBot = [{"role": "system","content": f"Hello, I am {Username}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

# Basic Google search using pywhatkit
def GoogleSearch(Topic):
    search(Topic)
    return True

# Function to generate content using AI and save it to a file.
def Content(Topic):

    # Nested function to open a file in Notepad.
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'  # Default text editor.
        subprocess.Popen([default_text_editor, File])  # Open the file in Notepad.

    # Nested function to generate content using the AI chatbot.
    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": f"{prompt}"})  # Add the user's prompt to messages.

        completion = client.chat.completions.create(
            model="mistral-8x7b-32768",  # Specify the AI model.
            messages=SystemChatBot + messages,  # Include system instructions and chat history.
            max_tokens=2048,  # Limit the maximum tokens in the response.
            temperature=0.7,  # Adjust response randomness.
            top_p=1,  # Use nucleus sampling for response diversity.
            stream=True,  # Enable streaming responses.
            stop=None  # Allow the model to determine stopping conditions.
        )

        Answer = ""  # Initialize an empty string for the response.

        # Process streamed response chunks.
        for chunk in completion:
            if chunk.choices[0].delta.content:  # Check for content in the current chunk.
                Answer += chunk.choices[0].delta.content  # Append the content to the answer.

        Answer = Answer.replace("</s>", "")  # Remove unwanted tokens from the response.
        messages.append({"role": "assistant", "content": Answer})  # Add the AI's response to messages.
        return Answer

    Topic: str = Topic.replace("Content ", "")  # Remove "Content" from the topic.
    ContentByAI = ContentWriterAI(Topic)  # Generate content using AI.

    # Save the generated content to a text file.
    with open(rf"Data\{Topic.lower().replace(' ', '')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI)  # Write the content to the file.
        file.close()

    OpenNotepad(rf"Data\{Topic.lower().replace(' ', '')}.txt")  # Open the file in Notepad.
    return True  # Indicate success.

# Function to construct and open a YouTube search URL
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"  # Format the search URL.
    webbrowser.open(Url4Search)  # Launch it in the browser.
    return True  # Indicate successful operation.

# Function to directly play a YouTube video using pywhatkit
def PlayYoutube(query):
    playonyt(query)  # Uses pywhatkit's helper to auto-play a video.
    return True

# Function to open an app or search for it if not installed
def OpenApp(app, sess=requests.session()):
    # Common websites mapping
    website_map = {
        "youtube": "https://www.youtube.com",
        "facebook": "https://www.facebook.com",
        "instagram": "https://www.instagram.com",
        "twitter": "https://www.twitter.com",
        "x": "https://www.x.com",
        "linkedin": "https://www.linkedin.com",
        "gmail": "https://www.gmail.com",
        "google": "https://www.google.com",
        "github": "https://www.github.com",
        "reddit": "https://www.reddit.com",
        "netflix": "https://www.netflix.com",
        "amazon": "https://www.amazon.com",
        "spotify": "https://www.spotify.com",
        "discord": "https://www.discord.com",
        "telegram": "https://web.telegram.org",
        "whatsapp": "https://web.whatsapp.com"
    }
    
    # Check if it's a known website
    app_lower = app.lower().strip()
    if app_lower in website_map:
        print(f"Opening website: {website_map[app_lower]}")
        webbrowser.open(website_map[app_lower])
        return True
    
    try:
        # Check if the app is actually a file path
        if os.path.exists(app):
            # If it's a file path, open it with the default application
            os.startfile(app)
            return True
        else:
            # Try to open as an application
            appopen(app, match_closest=True, output=True, throw_error=True)
            return True
    except Exception as e:
        print(f"Could not open {app} directly: {e}")
        
        # For file paths with spaces or special characters, try to handle them
        if " " in app and ("file" in app.lower() or "folder" in app.lower() or "download" in app.lower()):
            print(f"Attempting to handle file path: {app}")
            # Try to extract a more reasonable search term
            search_terms = app.split()
            # Remove common words that don't help with search
            filtered_terms = [term for term in search_terms if term.lower() not in 
                            ['file', 'folder', 'download', 'desktop', 'in', 'the', 'a', 'an', 'and', 'or']]
            if filtered_terms:
                search_query = " ".join(filtered_terms)
                print(f"Searching for: {search_query}")
                # Try to open the search query in browser
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
                return True
        
        # Nested helper to extract links from HTML
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')  # Parse with BeautifulSoup.
            links = soup.find_all('a', {'jsname': 'UWCkNb'})  # Select likely result anchors.
            return [link.get('href') for link in links]

        # Perform Google search and retrieve HTML
        def search_google(query):
            url = f"https://www.google.com/search?q={query}"  # Construct the URL.
            headers = {"User-Agent": useragent}  # Mimic browser behavior.
            response = sess.get(url, headers=headers)  # Make the HTTP request.
            if response.status_code == 200:
                return response.text  # Return page content on success.
            else:
                print("Failed to retrieve search results.")
                return None

        html = search_google(app)  # Try to find the app via Google if local open fails.

        if html:
            links = extract_links(html)
            if links:  # Check if links were found
                link = links[0]
                webopen(link)
                return True
            else:
                print(f"No download links found for {app}")
                return False
        else:
            print(f"Could not search for {app}")
            return False

# Function to close an application.
def closeApp(app):
    if "chrome" in app:
        pass  # Skip if the app is Chrome.
    else:
        try:
            close(app, match_closest=True, output=True, throw_error=True)  # Attempt to close the app.
            return True  # Indicate success.
        except:
            return False  # Indicate failure.

# Function to execute system volume commands.
def System(command):
    # Nested function to mute the system volume.
    def mute():
        keyboard.press_and_release("volume mute")

    # Nested function to unmute the system volume.
    def unmute():
        keyboard.press_and_release("volume mute")

    # Nested function to increase the system volume.
    def volume_up():
        keyboard.press_and_release("volume up")

    # Nested function to decrease the system volume.
    def volume_down():
        keyboard.press_and_release("volume down")

    # Execute the appropriate command based on input.
    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up()
    elif command == "volume down":
        volume_down()

    return True  # Indicate successful execution.

# Function to translate and execute user commands.
async def TranslateAndExecute(commands: list[str]):

    funcs = []  # List to store asynchronous tasks.

    for command in commands:

        if command.startswith("open "):  # Handle "open" commands
            if "open it" in command:  # Ignore "open it" commands.
                pass
            elif "open file" == command:  # Ignore "open file" commands.
                pass
            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs.append(fun)

        elif command.startswith("general "):  # Placeholder for general commands.
            pass

        elif command.startswith("realtime "):  # Placeholder for real-time commands.
            pass

        elif command.startswith("close "):  # Handle "close" commands.
            fun = asyncio.to_thread(closeApp, command.removeprefix("close "))
            funcs.append(fun)

        elif command.startswith("play "):  # Handle "play" commands.
            fun = asyncio.to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)

        elif command.startswith("content "):  # Handle "content" commands.
            fun = asyncio.to_thread(Content, command.removeprefix("content "))
            funcs.append(fun)

        elif command.startswith("google search "):  # Handle Google search commands.
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith("youtube search "):  # Handle YouTube search commands.
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith("system "):  # Handle system commands.
            fun = asyncio.to_thread(System, command.removeprefix("system "))
            funcs.append(fun) 

        else:
            print(f"No Function Found. For {command}")  # Print an error for unrecognized commands.

    if funcs:  # Only execute if there are functions to run
        try:
            results = await asyncio.gather(*funcs, return_exceptions=True)  # Execute all tasks concurrently with exception handling.
            
            for result in results:  # Process the results.
                if isinstance(result, Exception):
                    print(f"Command execution failed: {result}")
                    yield f"Error: {result}"
                elif isinstance(result, str):
                    yield result
                else:
                    yield result
        except Exception as e:
            print(f"Error in command execution: {e}")
            yield f"Error: {e}"
    else:
        yield "No commands to execute"

# Asynchronous function to automate command execution.
async def Automation(commands: list[str]):

    async for result in TranslateAndExecute(commands):  # Translate and execute commands.
        pass

    return True  # Indicate success.       