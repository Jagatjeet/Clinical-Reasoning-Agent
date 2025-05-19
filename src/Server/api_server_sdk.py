# mcp_server/server.py
import os
import io
from dotenv import load_dotenv
from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import uvicorn
from PIL import Image
from typing import Annotated
import requests
import base64
from PIL import Image
import matplotlib.pyplot as plt
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential

load_dotenv() 

# Connect to the AzureML workspace
credentials = DefaultAzureCredential()

subscription_id = "6c180dd2-1ec4-4fad-8ba8-1f2d8d67c129"
resource_group = "fmmg-mars-collab"
workspace = "fmmg-mars-collab"

ml_client = MLClient(
    DefaultAzureCredential(), subscription_id, resource_group, workspace
)

# Get endpoint details
endpoint = ml_client.online_endpoints.get("mi2ftgastro")
deployment = ml_client.online_deployments.get(
    name="classifier-gastrovision-purpl-1",
    endpoint_name="mi2ftgastro"
)


key = ml_client.online_endpoints.get_keys("mi2ftgastro").primary_key

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
    print(type(requests.post(
        endpoint.scoring_uri,
        json=data,
        headers={
            "Authorization": f"Bearer {key}",
            "azureml-model-deployment": deployment.name,
        },  # You may remove this if the traffic of the deployment is set to 100%
    )))

    return requests.post(
        endpoint.scoring_uri,
        json=data,
        headers={
            "Authorization": f"Bearer {key}",
            "azureml-model-deployment": deployment.name,
        },  # You may remove this if the traffic of the deployment is set to 100%
    ).json()



@app.post("/medical_image_processing")
async def process_image(file: Annotated [UploadFile, File()]):
    """
    Expects JSON of the form {"query": "..."}.
    Returns {"rows": [...]} with all non‑JSON types converted.
    """
    print(file.content_type)
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
            if(i > .05):
                disease = disease + str(text_index) + " " + labels[index] + "\n"
                text_index = text_index + 1
            index = index + 1

        #return{"filename":file.filename, "content_type":file.content_type, "message": f"The diseases detected are {disease}"}
        return{"message": f"The diseases detected are {disease}"}
    
    except Exception as e:
        raise HTTPException (status_code=500, detail=f"Error processing image: {e}")
    #return JSONResponse(content=jsonable_encoder(response.choices[0].message.content))

if __name__ == "__main__":
    uvicorn.run("api_server_sdk:app", host="0.0.0.0", port=8000, reload=True)