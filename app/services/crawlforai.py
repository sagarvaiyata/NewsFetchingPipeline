import asyncio
from crawl4ai import AsyncWebCrawler

async def fetch_markdown_crawl4ai(url: str) -> str:
    """
    Crawl the given URL with Crawl4AI and return the extracted Markdown.
    """
    # You can pass BrowserConfig, CrawlerRunConfig, etc. if you need to tweak behavior
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url)
        return result.markdown

