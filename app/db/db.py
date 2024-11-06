import psycopg2, os, requests

DB_HOST = "localhost"
DB_NAME = "main_db"
DB_USER = os.getenv("PG_USER")
DB_PASSWORD = os.getenv("PG_PW")
DB_PORT = os.getenv("PG_PORT")
WV_PORT = os.getenv("WV_PORT")


def connect_maindb() :
    return psycopg2.connect(
            host=DB_HOST,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )

vector_url = f"http://localhost:{WV_PORT}/v1"

def get_vector()