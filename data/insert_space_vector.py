# Select space data and do text embedding
# Then push to vector db
import psycopg2, os
from dotenv import load_dotenv
from openai import OpenAI
import vectordb

load_dotenv()
vectordb.delete_classes()
vectordb.create_classes()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("PG_USER")
DB_PASSWORD = os.getenv("PG_PW")
DB_PORT = os.getenv("PG_PORT")

client = OpenAI()

def get_embedding(text, model="text-embedding-3-small"):
   text = text.replace("\n", " ")
   return client.embeddings.create(input = [text], model=model).data[0].embedding
# df['ada_embedding'] = df.combined.apply(lambda x: get_embedding(x, model='text-embedding-3-small'))

conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
cur = conn.cursor()
cur.execute("""
            SELECT id, desc_summary, review_summary FROM spaces;
            """)

res = cur.fetchall()
for r in res :
    space_id, desc_summary, review_summary = r
    # print(str(space_id)+"\n"+desc_summary+review_summary+"\n")

    text_embedding = get_embedding(desc_summary + review_summary)
    # print(text_embedding)
    vectordb.add_space_property(space_id=space_id, text_embedding=text_embedding)
   

cur.close()
conn.close()