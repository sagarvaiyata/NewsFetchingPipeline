# import psycopg2
# from psycopg2.extras import RealDictCursor
# from app.config import RDS_HOST, RDS_DB, RDS_USER, RDS_PASSWORD, RDS_PORT

# def get_connection():
#     return psycopg2.connect(
#         host=RDS_HOST,
#         port=RDS_PORT,
#         database=RDS_DB,
#         user=RDS_USER,
#         password=RDS_PASSWORD
#     )

# def url_exists(url: str) -> bool:
#     conn = get_connection()
#     try:
#         with conn.cursor() as cur:
#             cur.execute("SELECT 1 FROM businesswire_articles WHERE url = %s", (url,))
#             return cur.fetchone() is not None
#     finally:
#         conn.close()

# def insert_doc(doc: dict):
#     conn = get_connection()
#     try:
#         with conn.cursor() as cur:
#             cur.execute("""
#                 INSERT INTO businesswire_articles (url, heading, ticker, date, content)
#                 VALUES (%s, %s, %s, %s, %s)
#                 ON CONFLICT (url) DO NOTHING
#             """, (
#                 doc["url"],
#                 doc["heading"],
#                 doc["ticker"],
#                 doc["date"],
#                 doc["content"]
#             ))
#             conn.commit()
#     finally:
#         conn.close()


import psycopg2
from psycopg2.extras import RealDictCursor
from app.config import RDS_HOST, RDS_DB, RDS_USER, RDS_PASSWORD, RDS_PORT
import json

def get_connection():
    return psycopg2.connect(
        host=RDS_HOST,
        port=RDS_PORT,
        database=RDS_DB,
        user=RDS_USER,
        password=RDS_PASSWORD
    )

def ensure_table_exists():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS businesswire_articles (
                    url TEXT PRIMARY KEY,
                    heading TEXT,
                    ticker TEXT,
                    date TEXT,
                    content TEXT
                )
            """)
            conn.commit()
    finally:
        conn.close()

def url_exists(url: str) -> bool:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM businesswire_articles WHERE url = %s", (url,))
            return cur.fetchone() is not None
    finally:
        conn.close()

def insert_doc(doc: dict):
    ensure_table_exists()  # Make sure table exists before inserting
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO businesswire_articles (url, heading, ticker, date, content)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (url) DO NOTHING
            """, (
                doc["url"],
                doc["heading"],
                doc["ticker"],
                doc["date"],
                json.dumps(doc["content"])  # Safely store as JSON string
            ))
            conn.commit()
    finally:
        conn.close()

def get_allowed_tickers() -> list[str]:
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT ticker FROM ticker_table")
            rows = cur.fetchall()
            return [row[0].upper() for row in rows if row[0]]
    finally:
        conn.close()
