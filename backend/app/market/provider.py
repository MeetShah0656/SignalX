from abc import ABC, abstractmethod
import datetime
from typing import List, Optional
from app.market.schemas import Quote, Candle

class MarketDataProvider(ABC):
    @abstractmethod
    async def get_latest_quote(self, symbol: str) -> Quote:
        """Fetch latest quote for the given symbol."""
        pass

    @abstractmethod
    async def get_historical_candles(
        self,
        symbol: str,
        timeframe: str = "5m",
        start_date: Optional[datetime.datetime] = None,
        end_date: Optional[datetime.datetime] = None,
        limit: int = 500
    ) -> List[Candle]:
        """Fetch historical candle data."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check provider connectivity status."""
        pass
