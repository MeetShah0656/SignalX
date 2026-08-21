from app.core.config import settings
from app.market.provider import MarketDataProvider
from app.market.mock_provider import MockMarketDataProvider
from app.market.live_provider import LiveMarketDataProvider
from app.market.kite_provider import KiteMarketDataProvider

def get_market_provider() -> MarketDataProvider:
    """
    Factory function returning the configured MarketDataProvider implementation.
    Supported settings.MARKET_DATA_PROVIDER values:
    - 'kite': Zerodha Kite Connect API Provider
    - 'yfinance': Yahoo Finance Provider
    - 'mock': Synthetic / Mock Data Provider (Default)
    """
    provider_type = settings.MARKET_DATA_PROVIDER.lower()
    
    if provider_type == "kite":
        return KiteMarketDataProvider()
    elif provider_type in ["yfinance", "live"]:
        return LiveMarketDataProvider(settings.SYMBOL)
    else:
        return MockMarketDataProvider()
