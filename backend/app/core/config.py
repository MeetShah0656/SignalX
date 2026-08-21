import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_ENV: str = "development"
    SECRET_KEY: str = "signalx-super-secret-key-change-in-production"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./signalx.db"

    # Market Data
    MARKET_DATA_PROVIDER: str = "mock"  # mock, yfinance, kite, broker
    MARKET_DATA_API_KEY: Optional[str] = ""
    MARKET_DATA_API_SECRET: Optional[str] = ""
    MARKET_DATA_BASE_URL: Optional[str] = ""

    # Zerodha Kite Connect Configuration
    KITE_API_KEY: Optional[str] = ""
    KITE_ACCESS_TOKEN: Optional[str] = ""
    KITE_INSTRUMENT_TOKEN: int = 256265  # Default NIFTY 50 Zerodha Instrument Token

    # Trading & Risk Configuration
    INITIAL_CAPITAL: float = 100000.0
    DEFAULT_TIMEFRAME: str = "5m"
    PREDICTION_HORIZON_MINUTES: int = 15

    BUY_THRESHOLD: float = 0.65
    SELL_THRESHOLD: float = 0.65
    MAX_RISK_PER_TRADE: float = 0.01  # 1%
    MAX_DAILY_LOSS: float = 0.02  # 2%
    SLIPPAGE_BPS: float = 5.0  # 5 bps
    MAX_OPEN_POSITIONS: int = 3  # Allow multiple concurrent scalp trades
    DEFAULT_LOTS: int = 2  # Fixed 2 Lots per trade
    LOT_SIZE: int = 25  # NIFTY lot size (25 shares per lot = 50 shares total)
    SCALP_PROFIT_PER_UNIT: float = 50.0  # Minimum ₹50 profit per unit target
    MAX_POSITION_DURATION_MINUTES: int = 10  # Soft 10-minute check (only closes if in profit)
    AUTO_TRADING_ENABLED: bool = True  # Continuous automated trading bot loop
    DEFAULT_TRADING_STRATEGY: str = "SMART_MONEY_ANTI_TRAP"  # SMART_MONEY_ANTI_TRAP, STANDARD_AI, HYBRID

    MAX_DATA_AGE_SECONDS: int = 15
    SYMBOL: str = "^NSEI"  # NIFTY 50 ticker symbol for yfinance / provider

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
