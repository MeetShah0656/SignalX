import datetime
from typing import List, Optional
import pandas as pd
import yfinance as yf
from app.market.provider import MarketDataProvider
from app.market.schemas import Quote, Candle
from app.market.mock_provider import MockMarketDataProvider
from app.core.logging import logger

class LiveMarketDataProvider(MarketDataProvider):
    def __init__(self, ticker_symbol: str = "^NSEI"):
        self.ticker_symbol = ticker_symbol
        self.fallback = MockMarketDataProvider()

    async def get_latest_quote(self, symbol: str) -> Quote:
        try:
            ticker = yf.Ticker(self.ticker_symbol)
            df = ticker.history(period="1d", interval="1m")
            if df.empty:
                logger.warning("Live data returned empty df, falling back to mock provider.")
                return await self.fallback.get_latest_quote(symbol)

            latest = df.iloc[-1]
            now = datetime.datetime.utcnow()
            close_price = round(float(latest["Close"]), 2)
            open_price = round(float(latest["Open"]), 2)
            high_price = round(float(latest["High"]), 2)
            low_price = round(float(latest["Low"]), 2)
            volume = float(latest["Volume"])

            bid = round(close_price - 0.25, 2)
            ask = round(close_price + 0.25, 2)

            return Quote(
                symbol=symbol,
                timestamp=now,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=volume,
                bid=bid,
                ask=ask,
                vwap=round((high_price + low_price + close_price) / 3, 2),
                oi=None,
                india_vix=13.5,
                is_live=True,
                provider="yfinance"
            )
        except Exception as e:
            logger.error(f"Error fetching live quote from yfinance: {e}")
            return await self.fallback.get_latest_quote(symbol)

    async def get_historical_candles(
        self,
        symbol: str,
        timeframe: str = "5m",
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
        limit: int = 500
    ) -> List[Candle]:
        try:
            interval = "5m"
            if timeframe == "1m":
                interval = "1m"
            elif timeframe == "15m":
                interval = "15m"

            ticker = yf.Ticker(self.ticker_symbol)
            df = ticker.history(period="7d", interval=interval)
            if df.empty:
                return await self.fallback.get_historical_candles(symbol, timeframe, start_date, end_date, limit)

            candles = []
            df = df.tail(limit)
            for idx, row in df.iterrows():
                ts = idx.to_pydatetime() if hasattr(idx, 'to_pydatetime') else datetime.datetime.utcnow()
                candles.append(Candle(
                    timestamp=ts,
                    symbol=symbol,
                    timeframe=timeframe,
                    open=round(float(row["Open"]), 2),
                    high=round(float(row["High"]), 2),
                    low=round(float(row["Low"]), 2),
                    close=round(float(row["Close"]), 2),
                    volume=float(row["Volume"])
                ))
            return candles
        except Exception as e:
            logger.error(f"Error fetching historical candles from yfinance: {e}")
            return await self.fallback.get_historical_candles(symbol, timeframe, start_date, end_date, limit)

    def is_connected(self) -> bool:
        return True
