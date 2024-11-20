# Select data from db
import psycopg2, os
from dotenv import load_dotenv
import csv

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

cur.execute("""
            SELECT * FROM spaces;
            """)



res = cur.fetchall()


cur.close()
conn.close()

print(res)