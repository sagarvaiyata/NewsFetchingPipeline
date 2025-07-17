from pymongo import MongoClient
from app.config import MONGO_URI, DB_NAME, COLLECTION_NAME

client = MongoClient(MONGO_URI)
collection = client[DB_NAME][COLLECTION_NAME]

def url_exists(url: str) -> bool:
    return collection.find_one({"url": url}) is not None

def insert_doc(doc: dict):
    collection.insert_one(doc)
