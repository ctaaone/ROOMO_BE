# Provide vector db api
import requests
import json
import uuid
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

WV_PORT = os.getenv("WV_PORT")
DB_HOST = os.getenv("DB_HOST")
WEAVIATE_URL = f"http://{DB_HOST}:{WV_PORT}/v1"


def get_embedding(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding
def delete_space_property(space_id):
    sid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(space_id+"s")))
    response = requests.delete(f'{WEAVIATE_URL}/objects/{sid}')

    if response.status_code == 204:
        print(f"Deleted space property with id: {space_id}")
    else:
        print(f"Failed to delete space property: {response.content}")
def add_space_property(space_id, text_embedding):
    sid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(space_id)+"s"))
    response = requests.post(f'{WEAVIATE_URL}/objects', json={
        "id" : sid,
        "class": "SpaceProperties",
        "properties": { "space_id": str(space_id) },
        "vector": text_embedding
    })

    if response.status_code == 200:
        print("Space property added:", { "vector": text_embedding }, response.content)
    else:
        print(f"Failed to add space property: {response.content}")
def update_space_property(space_id, text):
    delete_space_property(space_id=space_id)
    add_space_property(space_id=space_id, text_embedding=get_embedding(text=text))

def search_near_vector(user_text, space_ids) :
    if len(space_ids) == 0: return []

    user_vec = client.embeddings.create(input = [user_text.replace("\n", " ")], model="text-embedding-3-small").data[0].embedding
    # user_vec = get_user_preferences(user_id)
    space_list = [str(uuid.uuid5(uuid.NAMESPACE_DNS, str(s)+"s")) for s in space_ids]
    query = """
    {
      Get {
        SpaceProperties(
        nearVector: {vector: %s},
        where: {
            path: ["id"]
            operator: ContainsAny
            valueText: %s
        },
        limit: 4) {
            space_id
        }
      }
    }
    """ % (user_vec, json.dumps(space_list))

    response = requests.post(
        f"{WEAVIATE_URL}/graphql",
        json={"query": query}
    )
    if response.status_code == 200:
        similar_data = response.json()['data']['Get']['SpaceProperties']
        res = []
        if similar_data is not None :
            res = [int(e['space_id']) for e in similar_data]
        return res
    else:
        print("Failed to find similar data.")
        print("Status Code:", response.status_code)
        print("Response:", response.json())
        return []
