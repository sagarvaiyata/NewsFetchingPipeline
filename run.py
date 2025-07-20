import uvicorn
from dotenv import load_dotenv

load_dotenv()
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

# import psycopg2
# from app.config import RDS_HOST, RDS_PORT, RDS_DB, RDS_USER, RDS_PASSWORD

# conn = psycopg2.connect(
#     host=RDS_HOST,
#     port=RDS_PORT,
#     database=RDS_DB,
#     user=RDS_USER,
#     password=RDS_PASSWORD
# )

# def print_businesswire_articles():
#     try:
#         with conn.cursor() as cur:
#             cur.execute("""
#                 SELECT url, heading, ticker, date
#                 FROM businesswire_articles
#                 ORDER BY date DESC
#             """)
#             rows = cur.fetchall()
#             print("Businesswire Articles:")
#             for row in rows:
#                 print(f" - [{row[2]}] {row[1]}")
#                 print(f"   {row[3]}")
#                 print(f"     {row[0]}")
#                 print()
#     finally:
#         conn.close()

# def insert_ticker_table():
#     try:
#         with conn.cursor() as cur:
#             tickers = ["AAPL", "MCS", "DK", "NVT", "DIT", "FIX", "ORBN", "CCFN", "DKL"]

#             for t in tickers:
#                 cur.execute("""
#                     INSERT INTO ticker_table (ticker)
#                     VALUES (%s)
#                     ON CONFLICT (ticker) DO NOTHING
#                 """, (t,))
#             conn.commit()
#             print(f"✅ Inserted {len(tickers)} tickers.")
#     finally:
#         conn.close()

# def print_ticker_table():
#     try:
#         with conn.cursor() as cur:
#             cur.execute("SELECT ticker FROM ticker_table ORDER BY ticker")
#             rows = cur.fetchall()
#             print("📋 Current tickers in ticker_table:")
#             for row in rows:
#                 print(f" - {row[0]}")
#     finally:
#         conn.close()


# if __name__ == "__main__":
#     print_businesswire_articles()

