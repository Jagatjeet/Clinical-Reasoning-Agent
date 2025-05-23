import urllib.request
import json
from dotenv import load_dotenv
import os
import base64
import requests
import sys

load_dotenv()

# Request data goes here
# The example below assumes JSON formatting which may be updated
# depending on the format your endpoint expects.
# More information can be found here:
# https://docs.microsoft.com/azure/machine-learning/how-to-deploy-advanced-entry-script


system_prompt = "You are a helpful AI Assistant, designed to provided well-reasoned and detailed responses. You FIRST think about the reasoning process as an internal monologue and then provide the user with the answer. The reasoning process MUST BE enclosed within <think> and </think> tags."

#user_input = "Murphy&;s sign is seen in?\nOptions:\nA. Acute appendicitis\nB. Acute cholecystitis\nC. Acute pancreatitis\nD. Ectopic pregnancy\n"
user_input = "Which disease is more likely given the symptoms: Change in bowel habits, incomplete relief during bowel movement, rectal bleeding, blood in stool, belly pain, weakness, fatigue, and unintended weight loss? (Options: colorectal cancer or resected polyps)."
#user_input = "calculate 5+(21*50)/2"
user_prompt = "Instructions:\nThink step-by-step and answer the following multiple-choice question. The reasoning process and answer should be enclosed within <think> <\/think> and <answer> <\/answer> tags, respectively, in the answer i.e., <think> reasoning process here <\/think> <answer> detailed answer with logical, concise explanation <\/answer>.The final answer should be on a new line starting with the phrase '\''Final Answer: '\''. It should be one of '\''A'\'', '\''B'\'', '\''C'\'', '\''D'\''. No other outputs are allowed. Now, try to solve the following question through the above guidelines:\n\n"

prompt = user_prompt + user_input

data = {
    "messages": [
    {
    "role": "system",
    "content": system_prompt
    },
    {
    "role": "user",
    "content": prompt
    }
    ]
}

#print(type(data))

#print(data)

#sys.exit("End of program")

body = str.encode(json.dumps(data))

print(body)

#url = os.environ["API_URL_REASONING_MODEL_GRPO"]
url = os.environ["API_URL_REASONING_MODEL_BASE"]
# Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
#api_key = os.environ['API_KEY_REASONING_MODEL_GRPO']
api_key = os.environ['API_KEY_REASONING_MODEL_BASE']

if not api_key:
    raise Exception("A key should be provided to invoke the endpoint")


headers = {'Content-Type':'application/json', 'Accept': 'application/json', 'Authorization':('Bearer '+ api_key)}

#req = urllib.request.Request(url, body, headers)

try:
    response = requests.post(url, data=body, headers=headers)
    print(response.content)
    print(response.json())

except requests.exceptions.HTTPError as error:
    print("The request failed with status code: " + str(error.code))

    # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
    print(error.info())
    print(error.read().decode("utf8", 'ignore'))