from fastapi import APIRouter
from app.models import TickerInput
from app.services.firecrawl import scrape_markdown
from app.services.openai_client import call_openai
from app.services.mongo import url_exists, insert_doc

router = APIRouter()

@router.post("/run-scrape")
async def run_scrape(input: TickerInput):
    target_url = "https://www.businesswire.com/newsroom?region=1000400&language=en&subject=1000006"
    scrape_result = scrape_markdown(target_url)

    # Extract links + tickers
    prompt = f"""
    You are a JSON generator. Output *only* valid JSON.

    Extract every link from this markdown page:
    \"\"\"{scrape_result}\"\"\"

    For each item, return an object with:
    - "heading": the article title
    - "url": the link's href
    - "ticker": the company's stock ticker symbol, cleaned to **just the symbol** (e.g., "TDCB" instead of "OTCPINK: TDCB" or "NASDAQ: AAPL").

    If no ticker is found, return an empty string.

    Example output:
    [
        {{ "heading": "Some Article", "url": "https://...", "ticker": "TDCB" }},
        {{ "heading": "Another Article", "url": "https://...", "ticker": "" }}
    ]
    """
    docs = call_openai(prompt)
    print(docs)
    allowed = [t.upper() for t in input.ticker_codes]

    filtered_docs = [
        doc for doc in docs 
            if isinstance(doc.get("ticker"), str) and doc["ticker"].upper() in allowed
    ]   
    new_docs = []

    for item in filtered_docs:
        if url_exists(item["url"]):
            continue

        article_md = scrape_markdown(item["url"])

        print(f"Processing article: {item['url']}")

        content_prompt = f"""
        You are a JSON generator. Output *only* valid JSON.

        From this markdown news article:
        \"\"\"{article_md}\"\"\"

        Extract:
        - "date": publication date
        - "content": full body content along contacts
        """
        parsed = call_openai(content_prompt)

        item["date"] = parsed.get("date", "")
        item["content"] = parsed.get("content", "")
        insert_doc(item)

        # Make a copy and convert ObjectId to string if present
        item_clean = item.copy()
        if "_id" in item_clean:
            item_clean["_id"] = str(item_clean["_id"])
        new_docs.append(item_clean)


    return {
        "message": f"Scrape complete",
        "new_documents_count": len(new_docs),
        "new_documents": new_docs
    }
