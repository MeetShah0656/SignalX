import sys
import os
import asyncio
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.market.mock_provider import MockMarketDataProvider
from app.market.live_provider import LiveMarketDataProvider
from app.backtesting.engine import BacktestEngine
from app.core.config import settings
from app.core.logging import logger

async def main():
    logger.info("=== Starting NIFTY Strategy Backtest ===")
    
    if settings.MARKET_DATA_PROVIDER == "live" or settings.MARKET_DATA_PROVIDER == "yfinance":
        provider = LiveMarketDataProvider(settings.SYMBOL)
    else:
        provider = MockMarketDataProvider()

    candles = await provider.get_historical_candles("NIFTY 50", timeframe="5m", limit=500)
    logger.info(f"Loaded {len(candles)} candles for backtest.")

    engine = BacktestEngine(initial_capital=100000.0)
    results = engine.run_backtest(candles)

    metrics = results["metrics"]
    logger.info("=== Backtest Performance Results ===")
    logger.info(f"Initial Capital : INR {metrics['initial_capital']:.2f}")
    logger.info(f"Final Equity    : INR {metrics['final_equity']:.2f}")
    logger.info(f"Total Return    : {metrics['total_return']:.2f}%")
    logger.info(f"Win Rate        : {metrics['win_rate']:.2f}%")
    logger.info(f"Profit Factor   : {metrics['profit_factor']:.2f}")
    logger.info(f"Max Drawdown    : {metrics['max_drawdown']:.2f}%")
    logger.info(f"Sharpe Ratio    : {metrics['sharpe_ratio']:.2f}")
    logger.info(f"Total Trades    : {metrics['total_trades']}")

if __name__ == "__main__":
    asyncio.run(main())
