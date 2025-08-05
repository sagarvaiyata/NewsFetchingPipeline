# app/routes/your_router.py
from fastapi import APIRouter, HTTPException
from app.services.crawlforai import fetch_markdown_crawl4ai as scrape_markdown
from app.services.openai_client import call_openai
from app.services.rds import url_exists, insert_doc, get_allowed_tickers
from datetime import datetime
from zoneinfo import ZoneInfo
from crawl4ai import AsyncWebCrawler

router = APIRouter()

@router.get("/run-scrape")
async def run_scrape():
    # 1) scrape the listing page
    target_url = "https://www.businesswire.com/newsroom?region=1000400&language=en&subject=1000006"
    listing_md = await scrape_markdown(target_url)

    # Get current time in Eastern Time
    now_et = datetime.now(ZoneInfo("America/Toronto"))
    formatted_date = now_et.strftime("%b %d, %Y at %I:%M %p ET")

    # 2) build & call your LLM prompt
    prompt = f"""
        You are a JSON generator. Output *only* valid JSON.

        From this markdown:
        \"\"\"{listing_md}\"\"\"
        extract news articles. For each, return an object with:
        - "heading": the article title
        - "url": the href
        - "ticker": stock symbol only (e.g. "AAPL"; empty string if none)
        - "date": publication date & time as {formatted_date}
        - "fetched_at": the current time ({formatted_date})

        Output a JSON array of objects.
        """
    docs = call_openai(prompt)

    # 3) load allowed tickers
    allowed = {t.upper() for t in get_allowed_tickers()}

    new_docs = []
    # 4) iterate and optionally fetch full article
    async with AsyncWebCrawler() as crawler:
        for doc in docs:
            url    = doc.get("url", "")
            ticker = doc.get("ticker", "").upper()

            if url_exists(url):
                continue

            if ticker in allowed:
                # reuse the same crawler instance
                result = await crawler.arun(url=url)
                article_md = result.markdown
                content_prompt = f"""
                    You are a JSON generator. Output *only* valid JSON.

                    From this markdown news article:
                    \"\"\"{article_md}\"\"\"

                    Extract:
                    - "content": the full body of the press release (including contact info)
                    """
                parsed = call_openai(content_prompt)
                doc["content"] = parsed.get("content", "").strip()
            else:
                doc["content"] = None

            insert_doc(doc)
            new_docs.append(doc)

    return {
        "message": "Scrape complete",
        "new_documents_count": len(new_docs),
        "new_documents": new_docs,
    }

@router.get("/health", summary="Service health check")
async def health_check():
    try:
        _ = get_allowed_tickers()
    except Exception:
        raise HTTPException(status_code=503, detail="Database connection failed")
    return {"status": "ok"}
