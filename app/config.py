from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

DB_NAME = os.getenv("DB_NAME", "NewsScrapingDB")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "BusinessWire")

# Optional: validate required variables
required = {
    "FIRECRAWL_API_KEY": FIRECRAWL_API_KEY,
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "MONGO_URI": MONGO_URI,
}
missing = [key for key, val in required.items() if not val]
if missing:
    raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")
