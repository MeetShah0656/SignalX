import sys
import os
import asyncio

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.market.mock_provider import MockMarketDataProvider
from app.market.live_provider import LiveMarketDataProvider
from app.features.pipeline import build_feature_dataframe, generate_classification_targets
from app.ml.trainer import train_and_evaluate_models
from app.core.config import settings
from app.core.logging import logger

async def main():
    logger.info("=== Starting AI Model Training Pipeline ===")
    
    if settings.MARKET_DATA_PROVIDER == "live" or settings.MARKET_DATA_PROVIDER == "yfinance":
        provider = LiveMarketDataProvider(settings.SYMBOL)
    else:
        provider = MockMarketDataProvider()

    logger.info(f"Fetching historical candle data via provider: {provider.__class__.__name__}...")
    candles = await provider.get_historical_candles("NIFTY 50", timeframe="5m", limit=500)
    logger.info(f"Retrieved {len(candles)} historical candles.")

    logger.info("Calculating technical features and target labels...")
    df_features = build_feature_dataframe(candles)
    df_dataset = generate_classification_targets(df_features, horizon_candles=3, threshold=0.003)

    logger.info("Training and evaluating XGBoost, RandomForest, and LogisticRegression...")
    res = train_and_evaluate_models(df_dataset)

    logger.info("=== Training Pipeline Completed Successfully ===")
    logger.info(f"Selected Best Model: {res['model_name']} ({res['model_version']})")
    logger.info(f"Test Accuracy: {res['metrics']['accuracy'] * 100:.2f}%")
    logger.info(f"Test F1 Score: {res['metrics']['f1_score']:.4f}")

if __name__ == "__main__":
    asyncio.run(main())
