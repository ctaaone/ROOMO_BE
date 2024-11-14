import psycopg2, os
from dotenv import load_dotenv
import csv

roles="""

"""


load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("PG_USER")
DB_PASSWORD = os.getenv("PG_PW")
DB_PORT = os.getenv("PG_PORT")

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
        provider_id, space_name, price, max_capacity, address, space_type, abstract, *reviews = row

        print(reviews)
        # cur.execute("""
        #             INSERT INTO spaces (provider_id, name, address, abstract)
        #             VALUES (%s, %s, %s);
        #             """, (provider_id, space_name, address, abstract))
        


conn.commit()
cur.close()
conn.close()