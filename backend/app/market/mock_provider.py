import datetime
import random
import math
from typing import List, Optional
from app.market.provider import MarketDataProvider
from app.market.schemas import Quote, Candle

class MockMarketDataProvider(MarketDataProvider):
    def __init__(self, initial_price: float = 24685.40):
        self.current_price = initial_price
        self.symbol = "NIFTY 50"
        self.last_update = datetime.datetime.utcnow()
        self.volume_counter = 12500.0
        self.india_vix = 13.45

    async def get_latest_quote(self, symbol: str) -> Quote:
        now = datetime.datetime.utcnow()
        # Random walk drift with mean reversion
        change = random.normalvariate(0, 4.5)
        self.current_price = max(1000.0, round(self.current_price + change, 2))
        self.india_vix = max(8.0, round(self.india_vix + random.uniform(-0.1, 0.1), 2))
        
        spread = 0.50
        bid = round(self.current_price - spread / 2, 2)
        ask = round(self.current_price + spread / 2, 2)
        vwap = round(self.current_price + random.uniform(-1.0, 1.0), 2)
        
        self.last_update = now
        self.volume_counter += random.randint(100, 500)

        return Quote(
            symbol=symbol,
            timestamp=now,
            open=round(self.current_price - random.uniform(-2, 2), 2),
            high=round(self.current_price + random.uniform(0.5, 3.5), 2),
            low=round(self.current_price - random.uniform(0.5, 3.5), 2),
            close=self.current_price,
            volume=float(self.volume_counter),
            bid=bid,
            ask=ask,
            vwap=vwap,
            oi=28500000.0,
            india_vix=self.india_vix,
            is_live=False,
            provider="mock"
        )

    async def get_historical_candles(
        self,
        symbol: str,
        timeframe: str = "5m",
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
        limit: int = 500
    ) -> List[Candle]:
        candles: List[Candle] = []
        now = end_date or datetime.datetime.utcnow()
        
        tf_minutes = 5
        if timeframe == "1m":
            tf_minutes = 1
        elif timeframe == "15m":
            tf_minutes = 15

        price = self.current_price
        for i in range(limit, 0, -1):
            ts = now - datetime.timedelta(minutes=i * tf_minutes)
            drift = random.normalvariate(0.2, 8.0)
            open_p = price
            close_p = max(1000.0, round(open_p + drift, 2))
            high_p = max(open_p, close_p) + round(random.uniform(0.5, 5.0), 2)
            low_p = min(open_p, close_p) - round(random.uniform(0.5, 5.0), 2)
            volume = float(random.randint(5000, 25000))
            
            candles.append(Candle(
                timestamp=ts,
                symbol=symbol,
                timeframe=timeframe,
                open=open_p,
                high=high_p,
                low=low_p,
                close=close_p,
                volume=volume
            ))
            price = close_p
            
        return candles

    def is_connected(self) -> bool:
        return True
