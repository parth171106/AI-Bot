from googlesearch import search
from groq import Groq  # Importing the Groq library to use its API.
from json import load, dump  # Importing functions to read and write JSON files.
import json  # Import json for JSONDecodeError
import datetime  # Importing the datetime module for real-time date and time information.
from dotenv import dotenv_values  # Importing dotenv_values to read environment variables from a .env file.

# Load environment variables from the .env file.
env_vars = dotenv_values(".env")

# Retrieve environment variables for the chatbot configuration.
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client with the provided API key.
client = Groq(api_key=GroqAPIKey)

# Define the system instructions for the chatbot.
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which has real-time up-to-date information from the internet.
*** Provide Answers In a Professional Way, make sure to add full stops, commas, question marks, and use proper grammar.***
*** Just answer the question from the provided data in a professional way. ***"""

# Try to load the chat log from a JSON file, or create an empty one if it doesn't exist.
try:
    with open(r"Data\ChatLog.json", "r") as f:
        messages = load(f)
except:
    with open(r"Data\ChatLog.json", "w") as f:
        dump([], f)

# Function to perform a Google search and format the results.
def GoogleSearch(query):
    try:
        results = list(search(query, advanced=True, num_results=5))
        Answer = f"The search results for '{query}' are:\n[start]\n"

        if not results or len(results) == 0:
            Answer += "No search results found.\n"
        else:
            for i in results:
                title = getattr(i, 'title', 'No title')
                description = getattr(i, 'description', 'No description')
                Answer += f"Title: {title}\nDescription: {description}\n\n"

        Answer += "[end]"
        return Answer
    except Exception as e:
        print(f"Error in GoogleSearch function: {e}")
        raise  # Re-raise to be caught by caller

# Function to clean up the answer by removing empty lines.
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

# Predefined chatbot conversation system message and an initial user message.
SystemChatBot = [
    {"role": "system", "content": System},
    {"role": "user", "content": "Hi"},
    {"role": "assistant", "content": "Hello, how can I help you?"}
]

# Function to get real-time information like the current date and time.
def Information():
    data = ""
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")

    data += f"Use This Real-time Information if needed:\n"
    data += f"Day: {day}\n"
    data += f"Date: {date}\n"
    data += f"Month: {month}\n"
    data += f"Year: {year}\n"
    data += f"Time: {hour} hours, {minute} minutes, {second} seconds.\n"
    return data

# Function to handle real-time search and response generation.
def RealtimeSearchEngine(prompt):
    global SystemChatBot, messages

    search_appended = False  # Track if we appended to SystemChatBot
    
    try:
        # Load the chat log from the JSON file.
        try:
            with open(r"Data\ChatLog.json", "r") as f:
                messages = load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            messages = []
        
        messages.append({"role": "user", "content": f"{prompt}"})

        # Add Google search results to the system chatbot messages.
        try:
            search_results = GoogleSearch(prompt)
            # Check if search results are meaningful (not just [start][end])
            if search_results and len(search_results.strip()) > 20:
                SystemChatBot.append({"role": "system", "content": search_results})
            else:
                SystemChatBot.append({"role": "system", "content": "No search results available."})
            search_appended = True
        except Exception as e:
            print(f"Error in GoogleSearch: {e}")
            SystemChatBot.append({"role": "system", "content": "No search results available."})
            search_appended = True

        # Generate a response using the Groq client.
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=SystemChatBot + [{"role": "system", "content": Information()}] + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""

        # Concatenate response chunks from the streaming output.
        for chunk in completion:
            # Safely check for content
            if (chunk.choices and 
                len(chunk.choices) > 0 and 
                hasattr(chunk.choices[0], 'delta') and 
                chunk.choices[0].delta and 
                hasattr(chunk.choices[0].delta, 'content') and 
                chunk.choices[0].delta.content):
                Answer += chunk.choices[0].delta.content

        # Clean up the response.
        Answer = Answer.strip().replace("</s>", "")
        
        if not Answer or len(Answer.strip()) == 0:
            Answer = "I couldn't find relevant information. Please try rephrasing your question."
        
        messages.append({"role": "assistant", "content": Answer})

        # Save the updated chat log back to the JSON file.
        try:
            with open(r"Data\ChatLog.json", "w") as f:
                dump(messages, f, indent=4)
        except Exception as e:
            print(f"Error saving chat log: {e}")

        # Remove the most recent system message from the chatbot conversation.
        # Only pop if we actually appended something
        if search_appended and SystemChatBot and len(SystemChatBot) > 3:
            SystemChatBot.pop()
        
        return AnswerModifier(Answer=Answer)
    except Exception as e:
        print(f"Error in RealtimeSearchEngine: {e}")
        import traceback
        traceback.print_exc()
        
        # Clean up: remove appended search result if exception occurred
        if search_appended and SystemChatBot and len(SystemChatBot) > 3:
            SystemChatBot.pop()
        
        # Return a fallback message
        return "I'm sorry, I encountered an error while searching for information. Please try again."


# Main entry point of the program for interactive querying.
if __name__ == "__main__":
    while True:
        prompt = input("Enter your query: ")
        print(RealtimeSearchEngine(prompt))
    