# Provide vector db api
import requests
import json
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

WV_PORT = os.getenv("WV_PORT")
DB_HOST = os.getenv("DB_HOST")
WEAVIATE_URL = f"http://{DB_HOST}:{WV_PORT}/v1"

user_preferences_class = {
    "class": "UserPreferences",
    "properties": [
    ],
}
space_properties_class = {
    "class": "SpaceProperties",
    "properties": [
        {
            "name": "space_id",
            "dataType": ["text"]
        }
    ],
}

def create_classes():
    response = requests.post(f'{WEAVIATE_URL}/schema', json=user_preferences_class)
    if response.status_code == 200:
        print("Class 'UserPreferences' created.")
    else:
        print(f"Failed to create class: {response.content}")
    response = requests.post(f'{WEAVIATE_URL}/schema', json=space_properties_class)
    if response.status_code == 200:
        print("Class 'SpaceProperties' created.")
    else:
        print(f"Failed to create class: {response.content}")

def delete_classes():
    response = requests.delete(f'{WEAVIATE_URL}/schema/UserPreferences')
    if response.status_code == 204:
        print("Class 'UserPreferences' deleted.")
    else:
        print(f"Failed to delete class: {response.content}")
    response = requests.delete(f'{WEAVIATE_URL}/schema/SpaceProperties')
    if response.status_code == 204:
        print("Class 'SpaceProperties' deleted.")
    else:
        print(f"Failed to delete class: {response.content}")


## User
def add_user_preference(user_id, text_embedding):
    uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(user_id)+"u"))
    response = requests.post(f'{WEAVIATE_URL}/objects', json={
        "id" : uid,
        "class": "UserPreferences",
        "properties":{
        },
        "vector": text_embedding
    })

    if response.status_code == 200:
        print("User preference added:", { "vector": text_embedding })
    else:
        print(f"Failed to add user preference: {response.content}")

def get_all_user_preferences():
    response = requests.get(f'{WEAVIATE_URL}/objects?class=UserPreferences&include=vector')

    if response.status_code == 200:
        return response.json().get('objects', [])
    else:
        print(f"Failed to get user preferences: {response.content}")
        return []

def get_user_preferences(user_id):
    uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(user_id)+"u"))
    response = requests.get(f'{WEAVIATE_URL}/objects/UserPreferences/{uid}?include=vector')

    if response.status_code == 200:
        return response.json()['vector']
    else:
        print(f"Failed to get user preferences: {response.content}")
        return []

def delete_user_preference(user_id):
    uid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(user_id+"u")))
    response = requests.delete(f'{WEAVIATE_URL}/objects/{uid}')

    if response.status_code == 204:
        print(f"Deleted user preference with id: {user_id}")
    else:
        print(f"Failed to delete user preference: {response.content}")

## Space
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

def get_all_space_properties():
    response = requests.get(f'{WEAVIATE_URL}/objects?class=SpaceProperties&include=vector')

    if response.status_code == 200:
        return response.json().get('objects', [])
    else:
        print(f"Failed to get space properties: {response.content}")
        return []

def get_space_property(space_id):
    sid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(space_id)+"s"))
    response = requests.get(f'{WEAVIATE_URL}/objects/SpaceProperties/{sid}?include=vector')

    if response.status_code == 200:
        return response.json()['vector']
    else:
        print(f"Failed to get space property: {response.content}")
        return []

def delete_space_property(space_id):
    sid = str(uuid.uuid5(uuid.NAMESPACE_DNS, str(space_id+"s")))
    response = requests.delete(f'{WEAVIATE_URL}/objects/{sid}')

    if response.status_code == 204:
        print(f"Deleted space property with id: {space_id}")
    else:
        print(f"Failed to delete space property: {response.content}")


from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
client = OpenAI()
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
        limit: 10) {
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
            res = [e['space_id'] for e in similar_data]
        return res
    else:
        print("Failed to find similar data.")
        print("Status Code:", response.status_code)
        print("Response:", response.json())
        return []


# if __name__ == "__main__":
#     create_class()

#     add_user_preference("12345", [0.1, 0.2, 0.3])
#     add_user_preference("12346", [0.4, 0.5, 0.6])

#     add_space_property("12345", [0.1, 0.2, 0.3])
#     add_space_property("12346", [0.3, 0.4, 0.5])
#     print("User Preference : ", get_user_preferences("12345"))

#     all_preferences = get_all_user_preferences()
#     print("All User Preferences:", json.dumps(all_preferences, indent=2))
#     all_properties = get_all_space_properties()
#     print("All Space properties:", json.dumps(all_properties, indent=2))

#     # delete_user_preference("12345")
#     # all_preferences = get_all_user_preferences()
#     # print("All User Preferences:", json.dumps(all_preferences, indent=2))

#     search_near_vector("12345", ["12345", "12346"])