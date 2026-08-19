from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
import datetime
from app.market.live_provider import LiveMarketDataProvider
from app.market.mock_provider import MockMarketDataProvider
from app.core.config import settings

router = APIRouter(prefix="/api/market", tags=["Market Data"])

def get_provider():
    if settings.MARKET_DATA_PROVIDER == "live" or settings.MARKET_DATA_PROVIDER == "yfinance":
        return LiveMarketDataProvider(settings.SYMBOL)
    return MockMarketDataProvider()

@router.get("/nifty")
async def get_nifty_quote():
    provider = get_provider()
    quote = await provider.get_latest_quote("NIFTY 50")
    return quote.dict()

@router.get("/candles")
async def get_candles(
    timeframe: str = Query("5m", regex="^(1m|5m|15m)$"),
    limit: int = Query(200, ge=10, le=1000)
):
    provider = get_provider()
    candles = await provider.get_historical_candles(
        symbol="NIFTY 50",
        timeframe=timeframe,
        limit=limit
    )
    return [c.dict() for c in candles]
