import os
import json
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import BingGroundingTool, FunctionTool, ToolSet
from user_functions import user_functions
#from user_functions import calculate

from dotenv import load_dotenv
# Load variables from .env file
load_dotenv()

# Initialize the Azure AI Project Client
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)
# Initialize function tool with user-defined functions
#functions = FunctionTool(functions=user_functions)
functions = FunctionTool(user_functions)
#functions = FunctionTool({calculate})

# Combine tools into a toolset
toolset = ToolSet()
toolset.add(functions)

#Important - This is needed to make functions callable
project_client.agents.enable_auto_function_calls(toolset=toolset) 

# Create the agent with the combined toolset
with project_client:
    agent = project_client.agents.create_agent(
        model="gpt-4o",
        name="ClinicalReasoningAgentFunction",
        instructions="You are a reasoning assistant. For all questions you must call the symptom_analysis_diagnosis function. Breakdown and show the thinking steps before you get to the answer",
        toolset=toolset,
        headers={"x-ms-enable-preview": "true"}
    )
    print(f"Created agent, ID: {agent.id}")

    # Create a communication thread
    thread = project_client.agents.create_thread()
    print(f"Created thread, ID: {thread.id}")

    # User's message
    user_input = "calculate 5+(21*50)/2"
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=user_input,
    )
    print(f"Created message, ID: {message.id}")

    # Process the agent run
    run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Retrieve and display messages in chronological order
    messages_response = project_client.agents.list_messages(thread_id=thread.id)
    messages_data = messages_response["data"]
    sorted_messages = sorted(messages_data, key=lambda x: x["created_at"])

    print("\n--- Thread Messages (sorted) ---")
    for msg in sorted_messages:
        role = msg["role"].upper()
        content_blocks = msg.get("content", [])
        text_value = ""
        if content_blocks and content_blocks[0]["type"] == "text":
            text_value = content_blocks[0]["text"]["value"]
        print(f"{role}: {text_value}")

    # Delete the agent after completion
    #project_client.agents.delete_agent(agent.id)
    #print("Deleted agent")