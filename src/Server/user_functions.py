import json
from typing import Any, Callable, Set, Dict, List, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
import requests
import os

async def symptom_analysis_diagnosis(user_input: str) -> str:
    """
    Expects JSON of the form {"query": "..."}.
    Returns {"rows": [...]} with all non‑JSON types converted.
    """
    print("user_input:" + user_input)

    system_prompt = "You are a helpful AI Assistant, designed to provided well-reasoned and detailed responses. You FIRST think about the reasoning process as an internal monologue and then provide the user with the answer. The reasoning process MUST BE enclosed within <think> and </think> tags."
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

    body = str.encode(json.dumps(data))

    url = os.environ["API_URL_REASONING_MODEL"]
    # Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
    api_key = os.environ['API_KEY_REASONING_MODEL']

    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")


    headers = {'Content-Type':'application/json', 'Accept': 'application/json', 'Authorization':('Bearer '+ api_key)}

    #req = urllib.request.Request(url, body, headers)

    

    try:
        print("I am here")
        response = requests.post(url, data=body, headers=headers)
        print(response.text)
        print(type(response))
        return response.json()

    except requests.exceptions.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))


user_functions: Set[Callable[..., Any]] = {
     symptom_analysis_diagnosis
}
