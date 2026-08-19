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
    MARKET_DATA_PROVIDER: str = "mock"  # mock, yfinance, broker
    MARKET_DATA_API_KEY: Optional[str] = ""
    MARKET_DATA_API_SECRET: Optional[str] = ""
    MARKET_DATA_BASE_URL: Optional[str] = ""

    # Trading & Risk Configuration
    INITIAL_CAPITAL: float = 100000.0
    DEFAULT_TIMEFRAME: str = "5m"
    PREDICTION_HORIZON_MINUTES: int = 15

    BUY_THRESHOLD: float = 0.65
    SELL_THRESHOLD: float = 0.65
    MAX_RISK_PER_TRADE: float = 0.01  # 1%
    MAX_DAILY_LOSS: float = 0.02  # 2%
    SLIPPAGE_BPS: float = 5.0  # 5 bps
    MAX_OPEN_POSITIONS: int = 1

    MAX_DATA_AGE_SECONDS: int = 15
    SYMBOL: str = "^NSEI"  # NIFTY 50 ticker symbol for yfinance / provider

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
