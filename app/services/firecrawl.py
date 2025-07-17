from firecrawl import FirecrawlApp
from app.config import FIRECRAWL_API_KEY

firecrawl_client = FirecrawlApp(api_key=FIRECRAWL_API_KEY)

def scrape_markdown(url: str) -> str:
    return firecrawl_client.scrape_url(
        url,
        formats=["markdown"],
        proxy="stealth"
    )
