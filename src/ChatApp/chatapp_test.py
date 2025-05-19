import gradio as gr
import requests
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import BingGroundingTool
import os

from dotenv import load_dotenv
# Load variables from .env file
load_dotenv()
thread_id = ""

def process_chat(message, history):
    global thread_id
    print(history)
    print("History")
    print(len(history))
    print("History length")
    print(thread_id)
    print("Message")
    print(message)
    print("Message Length")
    print(len(message["text"]))
    print(len(message["files"]))
    thread_id=1
    return "Text Test"



demo = gr.ChatInterface(
    fn=process_chat, 
    type="messages", 
    examples=[
        {"text": "No files", "files": []}
    ], 
    multimodal=True,
    textbox=gr.MultimodalTextbox(file_count="multiple", file_types=["image"], sources=["upload", "microphone"])
)

demo.launch()