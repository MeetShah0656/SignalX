import asyncio
import datetime
from typing import List, Optional
import pandas as pd
import yfinance as yf
from app.market.provider import MarketDataProvider
from app.market.schemas import Quote, Candle
from app.market.mock_provider import MockMarketDataProvider
from app.core.logging import logger

def _fetch_yf_quote_details(ticker_symbol: str) -> dict:
    try:
        ticker = yf.Ticker(ticker_symbol)
        df_daily = ticker.history(period="5d", interval="1d")
        df_intraday = ticker.history(period="1d", interval="1m")
        if df_intraday.empty:
            df_intraday = ticker.history(period="5d", interval="1m")
        return {"daily": df_daily, "intraday": df_intraday}
    except Exception as e:
        logger.warning(f"yfinance quote details fetch failed: {e}")
        return {}

def _fetch_yf_history(ticker_symbol: str, period: str, interval: str) -> pd.DataFrame:
    try:
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period=period, interval=interval)
        if df.empty and period == "1d":
            df = ticker.history(period="5d", interval=interval)
        return df
    except Exception as e:
        logger.warning(f"yfinance network query failed: {e}")
        return pd.DataFrame()

class LiveMarketDataProvider(MarketDataProvider):
    def __init__(self, ticker_symbol: str = "^NSEI"):
        self.ticker_symbol = ticker_symbol
        self.fallback = MockMarketDataProvider(initial_price=24235.00)
        
        # Memory Caches
        self._cached_quote: Optional[Quote] = None
        self._quote_cache_time: Optional[datetime.datetime] = None
        self._cached_candles: dict = {}
        self._candles_cache_time: dict = {}

    async def get_latest_quote(self, symbol: str) -> Quote:
        now = datetime.datetime.utcnow()
        # Serve from 10-second cache if fresh
        if self._cached_quote and self._quote_cache_time:
            if (now - self._quote_cache_time).total_seconds() < 10.0:
                return self._cached_quote

        try:
            res = await asyncio.wait_for(
                asyncio.to_thread(_fetch_yf_quote_details, self.ticker_symbol),
                timeout=10.0
            )
            df_intraday = res.get("intraday", pd.DataFrame())
            df_daily = res.get("daily", pd.DataFrame())

            if df_intraday.empty:
                logger.warning("Live data returned empty df, falling back to mock provider.")
                return await self.fallback.get_latest_quote(symbol)

            latest = df_intraday.iloc[-1]
            close_price = round(float(latest["Close"]), 2)
            open_price = round(float(latest["Open"]), 2)
            high_price = round(float(latest["High"]), 2)
            low_price = round(float(latest["Low"]), 2)
            volume = float(latest["Volume"])

            # Keep fallback provider synced to latest real NSE close price
            self.fallback.current_price = close_price

            # Previous Close calculation from daily series
            prev_close = close_price
            if len(df_daily) >= 2:
                prev_close = round(float(df_daily.iloc[-2]["Close"]), 2)
            elif len(df_daily) == 1:
                prev_close = round(float(df_daily.iloc[0]["Close"]), 2)

            change = round(close_price - prev_close, 2)
            change_percent = round((change / prev_close) * 100, 2) if prev_close else 0.0

            bid = round(close_price - 0.25, 2)
            ask = round(close_price + 0.25, 2)

            quote = Quote(
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
                prev_close=prev_close,
                change=change,
                change_percent=change_percent,
                is_live=True,
                provider="yfinance"
            )

            # Update Cache
            self._cached_quote = quote
            self._quote_cache_time = now
            return quote
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
        now = datetime.datetime.utcnow()
        cache_key = f"{timeframe}_{limit}"
        if cache_key in self._cached_candles and cache_key in self._candles_cache_time:
            if (now - self._candles_cache_time[cache_key]).total_seconds() < 30.0:
                return self._cached_candles[cache_key]
        try:
            interval = "5m"
            period = "5d"
            if timeframe == "1m":
                interval = "1m"
                period = "5d"
            elif timeframe == "15m":
                interval = "15m"
                period = "1mo"

            df = await asyncio.wait_for(
                asyncio.to_thread(_fetch_yf_history, self.ticker_symbol, period, interval),
                timeout=10.0
            )
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
            self._cached_candles[cache_key] = candles
            self._candles_cache_time[cache_key] = now
            return candles
        except Exception as e:
            logger.error(f"Error fetching historical candles from yfinance: {e}")
            return await self.fallback.get_historical_candles(symbol, timeframe, start_date, end_date, limit)

    def is_connected(self) -> bool:
        return True
