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
    disease = ""
    symptoms = ""

    if (len(history)==0):
        thread_id=""

    if(len(message["files"]) > 0):
        print(message["files"][0])
        disease = image_processing_api(message["files"][0])
        thread_id=""
    
    if(len(message["text"]) > 0):
        symptoms = message["text"]

    diagnosis = diagnosis_agent(disease, symptoms)    
    return diagnosis

def image_processing_api(image_path):
    print(image_path)
    url = os.environ["API_SERVER_URL"]

    with open(image_path, 'rb') as img:
        img_data = img.read()
        #headers = {'Content-Type': 'image/jpeg'}
        files = {"file": ("image.jpg", img_data)}
        response = requests.post(url, files=files)

    print(response.status_code)
    print(response.text)
    return response.json()

def diagnosis_agent(disease, symptoms):
    global thread_id

    project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
    )

    # Create agent with the bing tool and process assistant run
    with project_client:
        agent = project_client.agents.get_agent(os.environ["AGENT_CLINICAL_REASONING"])
        
        print(f"Created agent, ID: {agent.id}")

        # Create thread for communication
        if(len(thread_id) == 0):
            thread = project_client.agents.create_thread()
            thread_id = thread.id
            print(f"Created thread, ID: {thread.id}")

        # Create prompt thread
        prompt = ""

        if(len(disease) > 0 and len(symptoms)>0):
            prompt = f"Given disease {disease} and symptoms {symptoms} which of the disease is more likely ?"

        elif(len(disease) > 0):
            prompt = f"Features have been extracted from an image. Extracted feature are {disease}. What are the diseases which have been identified in the features ?"

        elif(len(symptoms)>0):
            prompt = symptoms

        # Create message for thread
        message = project_client.agents.create_message(
            thread_id=thread_id,
            role="user",
            content=prompt,
        )
        print(f"Created message, ID: {message.id}")

        # Create and process agent run in thread with tools
        run = project_client.agents.create_and_process_run(thread_id=thread_id, agent_id=agent.id)
        print(f"Run finished with status: {run.status}")

        if run.status == "failed":
            print(f"Run failed: {run.last_error}")

        # Delete the assistant when done
        #project_client.agents.delete_agent(agent.id)
        #print("Deleted agent")

        # Fetch and log all messages in chronological order
        messages_response = project_client.agents.list_messages(thread_id=thread_id)
        messages_data = messages_response["data"]

        # Sort messages by creation time (ascending)
        sorted_messages = sorted(messages_data, key=lambda x: x["created_at"],reverse=True)

        print("\n--- Thread Messages (sorted) ---")
        print(sorted_messages[0]["content"][0]["text"]["value"])
        text = sorted_messages[0]["content"][0]["text"]["value"]
        return text
  

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