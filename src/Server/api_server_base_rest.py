# mcp_server/server.py
import os
import io
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
import uvicorn
from PIL import Image
from typing import Annotated
import base64
from PIL import Image
import json
import requests

load_dotenv() 

key = os.environ["API_KEY_IMAGE_PROCESSING"]

# Create the API app

app = FastAPI()

# Define the API functions

def make_request(image):
    data = {
        "input_data": {"columns": ["image"], "index": [0], "data": [[image]]},
        "params": {
            "image_standardization_jpeg_compression_ratio": 95,
            "image_standardization_image_size": 480,
        },
    }


    body = str.encode(json.dumps(data))

    url = os.environ["API_URL_IMAGE_PROCESSING"]
    # Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
    api_key = os.environ['API_KEY_IMAGE_PROCESSING']

    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")


    headers = {'Content-Type':'application/json', 'Accept': 'application/json', 'Authorization':('Bearer '+ api_key)}


    try:
        response = requests.post(url, json=data, headers=headers).json()

        return response
    except requests.exceptions.HTTPError as error:
        print("The request failed with status code: " + str(error.code))

        # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))



@app.post("/medical_image_processing")
async def process_image(file: Annotated [UploadFile, File()]):
    """
    Expects JSON of the form {"query": "..."}.
    Returns {"rows": [...]} with all non‑JSON types converted.
    """
    print(file)
    """
    if file.content_type != "image/jpeg":
        raise HTTPException (status_code=400, detail="Invalid file type. Only JPG images are allowed")
    """
    try:
        image_data = await file.read()
        im1 = Image.open(io.BytesIO(image_data))

        test_image = im1.save("image.jpg")
        test_image = os.path.abspath("image.jpg")
        print(test_image)

        with open(test_image, "rb") as f:
            image = base64.b64encode(f.read()).decode("utf-8")
            response = make_request(image)[0]

        labels, scores = zip(
            *[
                (r["label"], r["score"])
                for r in sorted(response, key=lambda x: x["score"], reverse=True)
            ][::-1]
        )

        index=0
        text_index=1
        disease = ""
        for i in scores:
            print(i)
            print(labels[index])
            if(i > .001):
                disease = disease + str(text_index) + " " + labels[index] + "\n"
                text_index = text_index + 1
            index = index + 1

        #return{"filename":file.filename, "content_type":file.content_type, "message": f"The diseases detected are {disease}"}
        return{"message": f"The diseases detected are {disease}"}
    
    except Exception as e:
        raise HTTPException (status_code=500, detail=f"Error processing image: {e}")
    #return JSONResponse(content=jsonable_encoder(response.choices[0].message.content))

@app.post("/symptom_analysis_diagnosis")
async def process_diagnosis(request: Request):
    """
    Expects JSON of the form {"query": "..."}.
    Returns {"rows": [...]} with all non‑JSON types converted.
    """
    body = await request.json()
    user_input = body.get("query")

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

    url = os.environ["API_URL_REASONING_MODEL_BASE"]
    # Replace this with the primary/secondary key, AMLToken, or Microsoft Entra ID token for the endpoint
    api_key = os.environ['API_KEY_REASONING_MODEL_BASE']

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

@app.get("/")
async def home_page():
    #Test accessibility of the ngrok url. Paste the url in grok and you should see "home"
    print("This is the home page")
    return "base"

if __name__ == "__main__":
    uvicorn.run("api_server_base_rest:app", host="0.0.0.0", port=8000, reload=True)
