import psycopg2
from config import Config

def fetch_data(col, table):
    conn = psycopg2.connect(Config.POSTGRES_URI)
    cur = conn.cursor()
    cur.execute(f'SELECT {col} FROM {table};')
    rows = cur.fetchall()
    conn.close()
    return [row[0] for row in rows]
