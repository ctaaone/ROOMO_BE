# Load reservations from csv file and insert to db
import psycopg2, os
from dotenv import load_dotenv
import csv
from datetime import datetime

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

# MONO User
cur.execute("""
            INSERT INTO users (id, name)
            VALUES (%s, %s)
            ON CONFLICT (id) DO NOTHING;
            """, ("0", "박땡땡",))

with open('reservations.csv', 'r', encoding='utf-8') as cvs_file :
    reader = csv.reader(cvs_file)
    next(reader) # Skip header

    for row in reader :
        user_id, space_id, start_time, end_time = row
        start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M")
        end_time = datetime.strptime(end_time, "%Y-%m-%d %H:%M")

        cur.execute("""
                    INSERT INTO reservations (user_id, space_id, start_time, end_time)
                    VALUES (%s, %s, %s, %s);
                    """, (user_id, space_id, start_time, end_time))

conn.commit()
cur.close()
conn.close()