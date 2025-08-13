from fastapi import APIRouter, HTTPException
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

from app.services.crawlforai import fetch_markdown_crawl4ai as scrape_markdown
from app.services.openai_client import call_openai
from app.services.rds import url_exists, insert_doc, get_allowed_tickers

router = APIRouter()

@router.get("/run-scrape")
async def run_scrape():
    # 1) scrape the listing page
    target_url = "https://www.businesswire.com/newsroom?region=1000400&language=en&subject=1000006"
    listing_md = await scrape_markdown(target_url)

    # 2) Current ET timestamp
    now_et = datetime.now(ZoneInfo("America/Toronto"))
    formatted_date = now_et.strftime("%b %d, %Y at %I:%M %p ET")

    prompt = f"""
    You are a JSON generator. Output *only* valid JSON.

    Below is ATX-style markdown scraped from a news listing page.

    Ignore navigation menus, headers, footers, ads, sidebars, comments, or any unrelated text. Focus only on actual news article entries.

    Markdown:
    \"\"\"{listing_md}\"\"\"

    For each news article, return a JSON object with the following fields:
    - "heading": the article title (string)
    - "url": the href (string)
    - "ticker": stock symbol only (e.g., "AAPL"); return an empty string if none
    - "date": the **exact** publication date and time **as shown in the markdown**.
    Do not alter formatting or substitute values.
    Date must not be missing, you will find it in specific publication markdown.
    - "fetched_at": the current time ({formatted_date})

    Output must be a JSON array of objects. Each object must reflect the information exactly as it appears in the markdown — especially the "date" field. Do not infer or fill in missing information.
    """.strip()

    # 4) call your sync OpenAI helper in a thread so it won't block
    loop = asyncio.get_running_loop()
    docs = await loop.run_in_executor(None, call_openai, prompt)

    # 5) load allowed tickers
    allowed = {t.upper() for t in get_allowed_tickers()}

    new_docs = []
    for doc in docs:
        url    = doc.get("url", "")
        ticker = doc.get("ticker", "").upper()

        # skip any URL we’ve already stored
        if url_exists(url):
            continue

        # if ticker is allowed, fetch the full article; otherwise leave content `None`
        if ticker in allowed:
            article_md = await scrape_markdown(url)

            content_prompt = f"""
                You are a JSON generator. Output *only* valid JSON.

                Below is ATX-style markdown scraped from a news article. **Ignore** any navigation menus, headers, footers, ads, sidebars, comments, or unrelated text—only extract the real article content.
                
                From this markdown news article:
                \"\"\"{article_md}\"\"\"

                Extract:
                - "content": the full body of the press release (including any contact info)
                """.strip()

            parsed = await loop.run_in_executor(None, call_openai, content_prompt)
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
