from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus )

from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import os

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?'''

subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search"]

def ShowDefaultChatIfNoChats():
    File = open(r'Data\ChatLog.json', "r", encoding='utf-8')
    if len(File.read()) < 5:
        with open(TempDirectoryPath('Database.data'), "w", encoding='utf-8') as file:
            file.write("")

        with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r'Data\ChatLog.json', "r", encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"
    
    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath('Database.data'), "w", encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    File = open(TempDirectoryPath('Database.data'), "r", encoding='utf-8')
    Data = File.read()
    if len(str(Data)) > 0:
        lines = Data.split('\n')
        result = '\n'.join(lines)
        File.close()
        File = open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8')
        File.write(result)
        File.close()

def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    try:
        SetAssistantStatus("Listening...")
        Query = SpeechRecognition()
        ShowTextToScreen(f"{Username} : {Query}")
        SetAssistantStatus("Thinking ...")
        
        # Get decision from the model with error handling
        try:
            Decision = FirstLayerDMM(Query)
        except Exception as e:
            print(f"Error in FirstLayerDMM: {e}")
            # Fallback to general query if decision-making fails
            Decision = [f"general {Query}"]
        
        # Ensure Decision is a list and not empty
        if not Decision or len(Decision) == 0:
            print("Warning: Decision is empty, defaulting to general query")
            Decision = [f"general {Query}"]

        print("")
        print(f"Decision : {Decision}")
        print("")

        G = any([i for i in Decision if isinstance(i, str) and i.startswith("general")])
        R = any([i for i in Decision if isinstance(i, str) and i.startswith("realtime")])

        Mearged_query = " and ".join(
            [" ".join(i.split()[1:]) for i in Decision if isinstance(i, str) and (i.startswith("general") or i.startswith("realtime"))]
        )

        for queries in Decision:
            if isinstance(queries, str) and "generate " in queries:
                ImageGenerationQuery = str(queries)
                ImageExecution = True

        for queries in Decision:
            if TaskExecution == False:
                if isinstance(queries, str) and any(queries.startswith(func) for func in Functions):
                    try:
                        run(Automation(list(Decision)))
                        TaskExecution = True
                    except Exception as e:
                        print(f"Automation error: {e}")
                        # Try to provide a helpful response
                        SetAssistantStatus("Sorry, I couldn't complete that task.")
                        ShowTextToScreen(f"{Assistantname} : I'm sorry, I couldn't complete that task. Please try a different approach.")
                        TextToSpeech("I'm sorry, I couldn't complete that task. Please try a different approach.")
                        TaskExecution = True

        if ImageExecution == True:
            with open(r"Frontend\Files\ImageGeneration.data", "w") as file:
                file.write(f"{ImageGenerationQuery},True")

            try:
                p1 = subprocess.Popen(
                    ['python', r'Backend\ImageGeneration.py'],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE, shell=False
                )
                subprocesses.append(p1)

            except Exception as e:
                print(f"Error starting ImageGeneration.py: {e}")

        # Fixed logic: (G and R) or R is equivalent to just R
        if R:
            try:
                SetAssistantStatus("Searching...")
                if Mearged_query:
                    Answer = RealtimeSearchEngine(QueryModifier(Mearged_query))
                else:
                    # Extract realtime query from Decision
                    realtime_queries = [i.replace("realtime ", "") for i in Decision if isinstance(i, str) and i.startswith("realtime")]
                    if realtime_queries:
                        Answer = RealtimeSearchEngine(QueryModifier(realtime_queries[0]))
                    else:
                        Answer = RealtimeSearchEngine(QueryModifier(Query))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True
            except Exception as e:
                print(f"Error in RealtimeSearchEngine: {e}")
                # Fallback to general chatbot
                SetAssistantStatus("Thinking...")
                Answer = ChatBot(QueryModifier(Query))
                ShowTextToScreen(f"{Assistantname} : {Answer}")
                SetAssistantStatus("Answering...")
                TextToSpeech(Answer)
                return True

        else:
            response_generated = False
            for Queries in Decision:
                if not isinstance(Queries, str):
                    continue
                    
                if "general" in Queries:
                    try:
                        SetAssistantStatus("Thinking...")
                        QueryFinal = Queries.replace("general ","")
                        Answer = ChatBot(QueryModifier(QueryFinal))
                        ShowTextToScreen(f"{Assistantname} : {Answer}")
                        SetAssistantStatus("Answering...")
                        TextToSpeech(Answer)
                        response_generated = True
                        return True
                    except Exception as e:
                        print(f"Error in ChatBot: {e}")
                        continue

                elif "realtime" in Queries:
                    try:
                        SetAssistantStatus("Searching...")
                        QueryFinal = Queries.replace("realtime ","")
                        Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
                        ShowTextToScreen(f"{Assistantname} : {Answer}")
                        SetAssistantStatus("Answering...")
                        TextToSpeech(Answer)
                        response_generated = True
                        return True
                    except Exception as e:
                        print(f"Error in RealtimeSearchEngine: {e}")
                        continue

                elif "exit" in Queries:
                    try:
                        QueryFinal = "Okay, Bye!"
                        Answer = ChatBot(QueryModifier(QueryFinal))
                        ShowTextToScreen(f"{Assistantname} : {Answer}")
                        SetAssistantStatus(" Answering... ")
                        TextToSpeech(Answer)
                        SetAssistantStatus(" Answering... ")
                        os._exit(1)
                    except Exception as e:
                        print(f"Error in exit handler: {e}")
                        os._exit(1)
            
            # If no response was generated, use fallback
            if not response_generated:
                print("Warning: No response generated, using fallback")
                try:
                    SetAssistantStatus("Thinking...")
                    Answer = ChatBot(QueryModifier(Query))
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering...")
                    TextToSpeech(Answer)
                    return True
                except Exception as e:
                    print(f"Error in fallback ChatBot: {e}")
                    error_message = "I'm sorry, I encountered an error processing your request. Please try again."
                    SetAssistantStatus("Error occurred")
                    ShowTextToScreen(f"{Assistantname} : {error_message}")
                    TextToSpeech(error_message)
                    return True
                    
    except Exception as e:
        print(f"Critical error in MainExecution: {e}")
        import traceback
        traceback.print_exc()
        error_message = "I'm sorry, I encountered an error. Please try again."
        SetAssistantStatus("Error occurred")
        ShowTextToScreen(f"{Assistantname} : {error_message}")
        try:
            TextToSpeech(error_message)
        except:
            pass
        return True

def FirstThread():
    while True:

        CurrentStatus = GetMicrophoneStatus()

        if CurrentStatus == "True":
            MainExecution()
            
        else:
            AIStatus = GetAssistantStatus()

            if "Available..." in AIStatus:
                sleep(0.1)

            else:
                SetAssistantStatus("Available...")

def SecondThread():

    GraphicalUserInterface()

if __name__ == "__main__":
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()

