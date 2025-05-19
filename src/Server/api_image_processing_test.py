from urllib.request import Request, urlopen
from urllib.error import HTTPError
import json
from dotenv import load_dotenv
import os
import base64
import requests
import gzip

load_dotenv()

# Request data goes here
# The example below assumes JSON formatting which may be updated
# depending on the format your endpoint expects.
# More information can be found here:
# https://docs.microsoft.com/azure/machine-learning/how-to-deploy-advanced-entry-script

test_image = os.path.abspath("image.jpg")
print(test_image)

with open(test_image, "rb") as f:
    image = base64.b64encode(f.read()).decode("utf-8")

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

#req = Request(url, body, headers)



try:
    response = requests.post(url, json=data, headers=headers).json()
    print(response)


    #response = gzip.decompress(urlopen(req).read()).decode('utf-8')
    #print(response.json())
except requests.exceptions.HTTPError as error:
    print("The request failed with status code: " + str(error.code))

    # Print the headers - they include the requert ID and the timestamp, which are useful for debugging the failure
    print(error.info())
    print(error.read().decode("utf8", 'ignore'))
