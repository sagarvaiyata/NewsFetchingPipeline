from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

DB_NAME = os.getenv("DB_NAME", "NewsScrapingDB")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "BusinessWire")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION")
DYNAMO_TABLE_NAME = os.getenv("DYNAMO_TABLE_NAME", "NewsScrapingDB")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

# Optional: validate required variables
required = {
    "FIRECRAWL_API_KEY": FIRECRAWL_API_KEY,
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "MONGO_URI": MONGO_URI,
}
missing = [key for key, val in required.items() if not val]
if missing:
    raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")
