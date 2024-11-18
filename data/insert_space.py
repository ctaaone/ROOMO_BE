# Load space data from csv file and summarize description and reviews
# Then push to db
import psycopg2, os
from dotenv import load_dotenv
from openai import OpenAI
import csv

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("PG_USER")
DB_PASSWORD = os.getenv("PG_PW")
DB_PORT = os.getenv("PG_PORT")

client = OpenAI()
conv1 = [{"role": "system", "content": "주어진 공간 설명을 요약해줘(핵심 내용을 포함해서 길어도 괜찮음). 요약 과정 등 미사여구는 생략하고 요약 결과만 출력해."}]
conv2 = [{"role": "system", "content": "주어진 공간 리뷰들을 요약해서 어떤 공간인지 간략히 설명해줘. 요약 과정 등 미사여구는 생략하고 요약 결과만 출력해."}]
conv3 = [{"role": "system", "content": "주어진 공간 설명과 리뷰를 요약해서 3줄정도로 해당 공간이 어떤 공간인지 요약해줘. ~입니다체를 사용해. 요약 과정 등 미사여구는 생략하고 요약 결과만 출력해."}]
def getGPT(content, conv):
    conv.append({"role": "user", "content": content})
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=conv
    )
    res = response.choices[0].message.content
    conv.append({"role": "assistant", "content": res})
    return res

conn = psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
cur = conn.cursor()

with open('spaces.csv', 'r', encoding='utf-8') as cvs_file :
    reader = csv.reader(cvs_file)
    next(reader) # Skip header

    for row in reader :
        provider_id, space_name, price, max_capacity, address, space_type, description, reserve_rule, *reviews = row
        
        description = f"공간 이름: {space_name}, 가격: {price}, 최대 인원수: {max_capacity}, 주소: {address}, 공간 종류: {space_type}\n" + description

        desc_summary = getGPT(content=description, conv=conv1)
        review_summary = getGPT(content='\n'.join(reviews), conv=conv2)
        abstract = getGPT(content=description + '\n리뷰 목록\n' + '\n'.join(reviews), conv=conv3)


        cur.execute("""
                    INSERT INTO providers (name)
                    VALUES (%s) RETURNING id;
                    """, ("김땡땡",))
        provider_id = cur.fetchone()[0]

        print("provier_id" + str(provider_id))
        print("desc_summary: "+desc_summary)
        print("review_summary: "+review_summary)
        print("abstract: "+abstract+"\n\n")
        cur.execute("""
                    INSERT INTO spaces (provider_id, name, address, abstract, desc_summary, review_summary, description, space_type, price, capacity)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """, (provider_id, space_name, address, abstract, desc_summary, review_summary, description, space_type, price, max_capacity))
        


conn.commit()
cur.close()
conn.close()