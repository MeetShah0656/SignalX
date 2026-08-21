import datetime
from typing import List, Optional
from app.market.provider import MarketDataProvider
from app.market.schemas import Quote, Candle
from app.market.mock_provider import MockMarketDataProvider
from app.core.config import settings
from app.core.logging import logger

try:
    from kiteconnect import KiteConnect
    KITE_AVAILABLE = True
except ImportError:
    KITE_AVAILABLE = False

class KiteMarketDataProvider(MarketDataProvider):
    """
    Zerodha Kite Connect Market Data Provider.
    Fetches real-time ticks/quotes and historical candle data from Kite Connect API.
    """
    def __init__(
        self,
        api_key: str = settings.KITE_API_KEY,
        access_token: str = settings.KITE_ACCESS_TOKEN,
        instrument_token: int = settings.KITE_INSTRUMENT_TOKEN
    ):
        self.api_key = api_key
        self.access_token = access_token
        self.instrument_token = instrument_token
        self.symbol_tradingsymbol = "NSE:NIFTY 50"
        self.fallback = MockMarketDataProvider()

        self.kite = None
        if KITE_AVAILABLE and self.api_key and self.access_token:
            try:
                self.kite = KiteConnect(api_key=self.api_key)
                self.kite.set_access_token(self.access_token)
                logger.info("Zerodha Kite Connect client initialized successfully.")
            except Exception as e:
                logger.error(f"Error initializing KiteConnect client: {e}")
                self.kite = None
        else:
            logger.warning("KiteConnect API Key or Access Token not configured. Using Mock Data fallback.")

    async def get_latest_quote(self, symbol: str) -> Quote:
        if not self.kite:
            return await self.fallback.get_latest_quote(symbol)

        try:
            # Fetch LTP / Quote from Kite Connect
            quote_data = self.kite.quote([self.symbol_tradingsymbol])
            if not quote_data or self.symbol_tradingsymbol not in quote_data:
                logger.warning("Kite quote returned empty, falling back to mock provider.")
                return await self.fallback.get_latest_quote(symbol)

            q = quote_data[self.symbol_tradingsymbol]
            ltp = round(float(q.get("last_price", 0.0)), 2)
            ohlc = q.get("ohlc", {})
            open_price = round(float(ohlc.get("open", ltp)), 2)
            high_price = round(float(ohlc.get("high", ltp)), 2)
            low_price = round(float(ohlc.get("low", ltp)), 2)
            close_price = ltp

            depth = q.get("depth", {})
            buy_depth = depth.get("buy", [])
            sell_depth = depth.get("sell", [])

            bid = round(float(buy_depth[0]["price"]), 2) if buy_depth else round(ltp - 0.25, 2)
            ask = round(float(sell_depth[0]["price"]), 2) if sell_depth else round(ltp + 0.25, 2)

            volume = float(q.get("volume", 0))
            oi = float(q.get("oi", 0))
            now = datetime.datetime.utcnow()

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
                vwap=round(float(q.get("average_price", ltp)), 2),
                oi=oi,
                india_vix=13.5,
                is_live=True,
                provider="kite"
            )
        except Exception as e:
            logger.error(f"Error fetching live quote from Kite Connect: {e}")
            return await self.fallback.get_latest_quote(symbol)

    async def get_historical_candles(
        self,
        symbol: str,
        timeframe: str = "5m",
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
        limit: int = 500
    ) -> List[Candle]:
        if not self.kite:
            return await self.fallback.get_historical_candles(symbol, timeframe, start_date, end_date, limit)

        try:
            interval_map = {
                "1m": "minute",
                "5m": "5minute",
                "15m": "15minute"
            }
            interval = interval_map.get(timeframe, "5minute")

            to_date = end_date or datetime.datetime.now()
            from_date = start_date or (to_date - datetime.timedelta(days=7))

            records = self.kite.historical_data(
                instrument_token=self.instrument_token,
                from_date=from_date.strftime("%Y-%m-%d %H:%M:%S"),
                to_date=to_date.strftime("%Y-%m-%d %H:%M:%S"),
                interval=interval
            )

            if not records:
                return await self.fallback.get_historical_candles(symbol, timeframe, start_date, end_date, limit)

            candles = []
            records = records[-limit:]
            for r in records:
                candles.append(Candle(
                    timestamp=r["date"],
                    symbol=symbol,
                    timeframe=timeframe,
                    open=round(float(r["open"]), 2),
                    high=round(float(r["high"]), 2),
                    low=round(float(r["low"]), 2),
                    close=round(float(r["close"]), 2),
                    volume=float(r["volume"])
                ))
            return candles
        except Exception as e:
            logger.error(f"Error fetching historical candles from Kite Connect: {e}")
            return await self.fallback.get_historical_candles(symbol, timeframe, start_date, end_date, limit)

    def is_connected(self) -> bool:
        return self.kite is not None
