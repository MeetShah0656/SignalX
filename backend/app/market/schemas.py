import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

class Quote(BaseModel):
    symbol: str
    timestamp: datetime.datetime
    open: float
    high: float
    low: float
    close: float  # Last Traded Price (LTP)
    volume: float
    bid: Optional[float] = None
    ask: Optional[float] = None
    vwap: Optional[float] = None
    oi: Optional[float] = None
    india_vix: Optional[float] = None
    prev_close: Optional[float] = None
    change: Optional[float] = None
    change_percent: Optional[float] = None
    is_live: bool = True
    provider: str = "mock"

class Candle(BaseModel):
    timestamp: datetime.datetime
    symbol: str
    timeframe: str = "5m"
    open: float
    high: float
    low: float
    close: float
    volume: float

class MarketStatus(BaseModel):
    is_open: bool
    status: str  # MARKET_OPEN, MARKET_CLOSED, PRE_OPEN, POST_MARKET, HOLIDAY
    timezone: str = "Asia/Kolkata"
    current_time: str
