# from fastapi import APIRouter
# from app.models import TickerInput
# from app.services.firecrawl import scrape_markdown
# from app.services.openai_client import call_openai
# # from app.services.mongo import url_exists, insert_doc # uncomment if using MongoDB
# # from app.services.dynamo import url_exists, insert_doc
# from app.services.rds import url_exists, insert_doc, get_allowed_tickers  # Use RDS for PostgreSQL

# router = APIRouter()

# # @router.post("/run-scrape")
# # async def run_scrape(input: TickerInput):
# #     target_url = "https://www.businesswire.com/newsroom?region=1000400&language=en&subject=1000006"
# #     scrape_result = scrape_markdown(target_url)

# #     # Extract links + tickers
# #     prompt = f"""
# #     You are a JSON generator. Output *only* valid JSON.

# #     Extract every link from this markdown page:
# #     \"\"\"{scrape_result}\"\"\"

# #     For each item, return an object with:
# #     - "heading": the article title
# #     - "url": the link's href
# #     - "ticker": the company's stock ticker symbol, cleaned to **just the symbol** (e.g., "TDCB" instead of "OTCPINK: TDCB" or "NASDAQ: AAPL").

# #     If no ticker is found, return an empty string.

# #     Example output:
# #     [
# #         {{ "heading": "Some Article", "url": "https://...", "ticker": "TDCB" }},
# #         {{ "heading": "Another Article", "url": "https://...", "ticker": "" }}
# #     ]
# #     """
# #     docs = call_openai(prompt)
# #     print(docs)
# #     allowed = [t.upper() for t in input.ticker_codes]

# #     filtered_docs = [
# #         doc for doc in docs 
# #             if isinstance(doc.get("ticker"), str) and doc["ticker"].upper() in allowed
# #     ]   
# #     new_docs = []

# #     for item in filtered_docs:
# #         if url_exists(item["url"]):
# #             print(f"Skipping existing URL: {item['url']}")
# #             continue

# #         article_md = scrape_markdown(item["url"])

# #         print(f"Processing article: {item['url']}")

# #         content_prompt = f"""
# #         You are a JSON generator. Output *only* valid JSON.

# #         From this markdown news article:
# #         \"\"\"{article_md}\"\"\"

# #         Extract:
# #         - "date": publication date and time with the format Jul 18, 2025 at 11:00 AM ET

# #         - "content": full body content along with contacts
# #         """
# #         parsed = call_openai(content_prompt)

# #         item["date"] = parsed.get("date", "")
# #         item["content"] = parsed.get("content", "")
# #         insert_doc(item)

# #         # Make a copy and convert ObjectId to string if present
# #         item_clean = item.copy()
# #         if "_id" in item_clean:
# #             item_clean["_id"] = str(item_clean["_id"])
# #         new_docs.append(item_clean)
        


# #     return {
# #         "message": f"Scrape complete",
# #         "new_documents_count": len(new_docs),
# #         "new_documents": new_docs
# #     }

# @router.post("/run-scrape")
# async def run_scrape():
#     target_url = "https://www.businesswire.com/newsroom?region=1000400&language=en&subject=1000006"
#     scrape_result = scrape_markdown(target_url)

#     # Call OpenAI to extract links and tickers
#     prompt = f"""
#     You are a JSON generator. Output *only* valid JSON.

#     Extract every link from this markdown page:
#     \"\"\"{scrape_result}\"\"\"

#     For each item, return an object with:
#     - "heading": the article title
#     - "url": the link's href
#     - "ticker": the company's stock ticker symbol, cleaned to **just the symbol** (e.g., "TDCB" instead of "OTCPINK: TDCB" or "NASDAQ: AAPL")
#     - "date": publication date and time with the format Jul 18, 2025 at 11:00 AM ET

#     If no ticker is found, return an empty string.

#     Example output:
#     [
#         {{ "heading": "Some Article", "url": "https://...", "ticker": "TDCB" }},
#         {{ "heading": "Another Article", "url": "https://...", "ticker": "" }}
#     ]
#     """
#     docs = call_openai(prompt)
#     print(docs)

#     allowed = get_allowed_tickers()
#     print(f"Allowed tickers from DB: {allowed}")

#     filtered_docs = [
#         doc for doc in docs
#         if isinstance(doc.get("ticker"), str) and doc["ticker"].upper() in allowed
#     ]

#     new_docs = []

#     for item in filtered_docs:
#         if url_exists(item["url"]):
#             print(f"Skipping existing URL: {item['url']}")
#             continue
        
#         new_docs.append(item)

#         # article_md = scrape_markdown(item["url"])
#         # print(f"Processing article: {item['url']}")

#         # content_prompt = f"""
#         # You are a JSON generator. Output *only* valid JSON.

#         # From this markdown news article:
#         # \"\"\"{article_md}\"\"\"

#         # Extract:
#         # - "date": publication date and time with the format Jul 18, 2025 at 11:00 AM ET
#         # - "content": full body content along with contacts
#         # """
#         # parsed = call_openai(content_prompt)

#         # item["date"] = parsed.get("date", "")
#         # item["content"] = parsed.get("content", "")
#         # insert_doc(item)

#         # item_clean = item.copy()
#         # if "_id" in item_clean:
#         #     item_clean["_id"] = str(item_clean["_id"])
#         # new_docs.append(item_clean)

#     return {
#         "message": "Scrape complete",
#         "new_documents_count": len(new_docs),
#         "new_documents": new_docs
#     }


from fastapi import APIRouter
from app.models import TickerInput
from app.services.firecrawl import scrape_markdown
from app.services.openai_client import call_openai
from app.services.rds import url_exists, insert_doc, get_allowed_tickers

router = APIRouter()

@router.post("/run-scrape")
async def run_scrape():
    # 1) scrape the listing page
    target_url = "https://www.businesswire.com/newsroom?region=1000400&language=en&subject=1000006"
    listing_md = scrape_markdown(target_url)

    # 2) one OpenAI call to extract heading/url/ticker
    prompt = f"""
    You are a JSON generator. Output *only* valid JSON.

    From this markdown:
    \"\"\"{listing_md}\"\"\", extract every link.
    For each, return an object with:
      - "heading": the article title
      - "url": the href
      - "ticker": stock symbol only (e.g. "AAPL", not "NASDAQ: AAPL"). Empty string if none.
      - "date": publication date and time with the format Jul 18, 2025 at 11:00 AM ET

    Output an array of objects.
    """
    docs = call_openai(prompt)
    # docs == [ { "heading":..., "url":..., "ticker":... }, … ]

    # 3) optional: filter against your “allowed tickers” table
    allowed = {t.upper() for t in get_allowed_tickers()}
    filtered = [
        d for d in docs
        if d.get("ticker", "").upper() in allowed
    ]

    # 4) remove duplicates & insert new
    new_docs = []
    for doc in filtered:
        if url_exists(doc["url"]):
            # already in DB → skip
            continue
        insert_doc(doc)
        new_docs.append(doc)

    return {
        "message": "Scrape complete",
        "new_documents_count": len(new_docs),
        "new_documents": new_docs
    }
