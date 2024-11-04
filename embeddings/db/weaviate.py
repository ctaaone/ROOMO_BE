import requests
import json
from config import Config

def save_to_vectordb(vector, space_id):
    weaviate_data = {
        "class": "SpaceAttr",
        "properties": {
            "space_id": space_id,
            "vector": vector
        }
    }
    response = requests.post(
        f"{Config.WEAVIATE_URL}/v1/objects",
        headers={"Content-Type": "application/json"},
        data=json.dumps(weaviate_data)
    )
    return response.json()
