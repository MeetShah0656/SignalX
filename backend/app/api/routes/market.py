from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
import datetime
from app.market.factory import get_market_provider

router = APIRouter(prefix="/api/market", tags=["Market Data"])

@router.get("/nifty")
async def get_nifty_quote():
    provider = get_market_provider()
    quote = await provider.get_latest_quote("NIFTY 50")
    return quote.dict()

@router.get("/candles")
async def get_candles(
    timeframe: str = Query("5m", pattern="^(1m|5m|15m)$"),
    limit: int = Query(200, ge=10, le=1000)
):
    provider = get_market_provider()
    candles = await provider.get_historical_candles(
        symbol="NIFTY 50",
        timeframe=timeframe,
        limit=limit
    )
    return [c.dict() for c in candles]
