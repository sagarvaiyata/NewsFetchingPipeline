from fastapi import FastAPI
from app.routes import scrape

app = FastAPI()
app.include_router(scrape.router)
