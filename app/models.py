from pydantic import BaseModel
from typing import List

class TickerInput(BaseModel):
    ticker_codes: List[str]
