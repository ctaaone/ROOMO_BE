# Select space data and do text embedding
# Then push to vector db
import psycopg2, os
from dotenv import load_dotenv
from openai import OpenAI
import vectordb

load_dotenv()

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


def insert_vector() :
    vectordb.delete_classes()
    vectordb.create_classes()

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
        space_id = str(space_id)
        # print(str(space_id)+"\n"+desc_summary+review_summary+"\n")

        if space_id == "1" or space_id == "2" :
            desc_summary = "조명이 화려함. 아주 화려한 조명이 있다. 조명이 예쁜 연습실, 화려한 조명을 갖고 있는 연습실 " + desc_summary
        if space_id == "3" or space_id == "4" :
            desc_summary = "공간이 넓음. 아주 넓은 공간의 연습실이다. 공간이 넓은 연습실이다. 넓은 연습실. 대형 연습실이다. 크기가 크다. 단체 연습에 적합하다. 단체 연습실." + desc_summary
        if space_id == "5" or space_id == "6" :
            desc_summary = "바닥이 탄성 마루이다. 탄성 마루인 바닥 재질. 바닥 재질이 탄성 마루인 연습실, 탄성 마루를 바닥 재질로 갖고 있는 연습실." + desc_summary
        if space_id == "7" or space_id == "8" :
            desc_summary = "방음이 잘됨. 아주 방음이 잘되는 연습실. 연습실에 방음 장치가 잘 되어 있다. 좋은 방음 시설을 갖고 있는 연습실이다." + desc_summary

        text_embedding = get_embedding(desc_summary + review_summary)
        # print(text_embedding)
        vectordb.add_space_property(space_id=space_id, text_embedding=text_embedding)
    

    cur.close()
    conn.close()

if __name__ == '__main__':
    insert_vector()
