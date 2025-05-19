import gradio as gr
import requests
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import BingGroundingTool
import os
import random

from dotenv import load_dotenv
# Load variables from .env file
load_dotenv()
thread_id = ""

PROMPT_TEMPLATE = """Instructions:
Think step-by-step and answer the following multiple-choice question. The reasoning process and answer should be enclosed within <think> </think> and <answer> </answer> tags, respectively, in the answer i.e., <think> reasoning process here </think> <answer> detailed answer with logical, concise explanation </answer>.The final answer should be on a new line starting with the phrase 'Final Answer: '. It should be one of 'A', 'B', 'C', 'D'. No other outputs are allowed. Now, try to solve the following question through the above guidelines:

Question:

Observed Symptoms:
{symptoms}

What is the prognosis 

Options:
{options_str}
"""



def apply_template(symptom_str, ref_disease, neg_diseases): 

    options = [ ref_disease ] + neg_diseases
    options_status = [ True, False, False, False ]

    options_with_status = list(zip(options, options_status))
    random.shuffle(options_with_status)
    choices=['A', 'B', 'C', 'D']

    options_detailed = [ (option, status, choice, f"{choice}. {option}") 
                            for (option, status), choice in zip(options_with_status, choices) ]

    options_str = '\n'.join([ x[3] for x in options_detailed ])                           

    prompt = PROMPT_TEMPLATE.format(symptoms=symptom_str, options_str=options_str)

    options_ref = list(filter(lambda x: x[1] is True, options_detailed))
    assert(len(options_ref)==1)
    ref = options_ref[0][2]

    return { "prompt": prompt, "ref": ref, }

def process_chat(message, history):
    global thread_id
    #disease = ""
    global disease
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
        agent = project_client.agents.get_agent(os.environ["AGENT_CLINICAL_REASONING_GRPO"])
        
        print(f"Created agent, ID: {agent.id}")

        # Create thread for communication
        if(len(thread_id) == 0):
            thread = project_client.agents.create_thread()
            thread_id = thread.id
            print(f"Created thread, ID: {thread.id}")

        # Create prompt thread
        prompt = ""

        if(len(disease) > 0 and len(symptoms)>0):
            prompt = f"Given disease {disease} and symptoms {symptoms} which of the diseases is most likely ? Choose one of them"

        elif(len(disease) > 0):
            prompt = f"Features have been extracted from an image. Extracted feature are {disease}. What are the diseases which have been identified in the features ? The diseases should be listed with the prefixes 'A', 'B', 'C', 'D'"
            
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
    title = "Clinical Agent - Reasoning Model"
    type="messages", 
    examples=[
        {"text": "No files", "files": []}
    ], 
    multimodal=True,
    textbox=gr.MultimodalTextbox(file_count="multiple", file_types=["image"], sources=["upload", "microphone"])
)

demo.launch()