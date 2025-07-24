from fastapi import APIRouter, HTTPException
from app.models import TickerInput
from app.services.firecrawl import scrape_markdown
from app.services.openai_client import call_openai
from app.services.rds import url_exists, insert_doc, get_allowed_tickers

router = APIRouter()

@router.get("/run-scrape")
async def run_scrape():
    # 1) scrape the listing page
    target_url = "https://www.businesswire.com/newsroom?region=1000400&language=en&subject=1000006"
    listing_md = scrape_markdown(target_url)

    # 2) extract heading/url/ticker/date in one shot
    prompt = f"""
    You are a JSON generator. Output *only* valid JSON.

    From this markdown:
    \"\"\"{listing_md}\"\"\"
    extract every link. For each, return an object with:
      - "heading": the article title
      - "url": the href
      - "ticker": stock symbol only (e.g. "AAPL", not "NASDAQ: AAPL"). Empty string if none.
      - "date": publication date and time with the format Jul 18, 2025 at 11:00 AM ET

    Output a JSON array of objects.
    """
    docs = call_openai(prompt)
    # docs == [ {"heading":…, "url":…, "ticker":…, "date":…}, … ]

    # 3) load your allowed ticker set once
    allowed = {t.upper() for t in get_allowed_tickers()}

    new_docs = []
    for doc in docs:
        url    = doc.get("url", "")
        ticker = doc.get("ticker", "").upper()

        # skip any URL we’ve already stored
        if url_exists(url):
            continue

        # if ticker is in your table, pull full content; else set content to None
        if ticker in allowed:
            article_md = scrape_markdown(url)
            content_prompt = f"""
            You are a JSON generator. Output *only* valid JSON.

            From this markdown news article:
            \"\"\"{article_md}\"\"\"

            Extract:
              - "content": the full body of the press release (including any contact info)
            """
            parsed = call_openai(content_prompt)
            doc["content"] = parsed.get("content", "").strip()
        else:
            doc["content"] = None

        # insert and collect for response
        insert_doc(doc)
        new_docs.append(doc)

    return {
        "message": "Scrape complete",
        "new_documents_count": len(new_docs),
        "new_documents": new_docs
    }

@router.get("/health", summary="Service health check")
async def health_check():
    """
    - Verifies that the application can talk to the database.
    - Returns 200 OK if healthy, 503 Service Unavailable if not.
    """
    try:
        # simple ping to your ticker table
        _ = get_allowed_tickers()
    except Exception as e:
        # DB error → unhealthy
        raise HTTPException(status_code=503, detail="Database connection failed")
    return {"status": "ok"}