from fastapi import APIRouter, Depends
from app.market.live_provider import LiveMarketDataProvider
from app.market.mock_provider import MockMarketDataProvider
from app.features.pipeline import build_feature_dataframe, FEATURE_COLUMNS
from app.ml.predictor import predictor
from app.core.config import settings

router = APIRouter(prefix="/api/prediction", tags=["Predictions"])

def get_provider():
    if settings.MARKET_DATA_PROVIDER == "live" or settings.MARKET_DATA_PROVIDER == "yfinance":
        return LiveMarketDataProvider(settings.SYMBOL)
    return MockMarketDataProvider()

@router.get("/latest")
async def get_latest_prediction():
    provider = get_provider()
    candles = await provider.get_historical_candles("NIFTY 50", timeframe="5m", limit=100)
    df_features = build_feature_dataframe(candles)

    if df_features.empty or len(df_features) < 20:
        return {
            "status": "INSUFFICIENT_DATA",
            "signal": "HOLD",
            "buy_probability": 0.0,
            "sell_probability": 0.0,
            "hold_probability": 1.0,
            "confidence": 0.0,
            "expected_return": 0.0
        }

    latest_row = df_features.iloc[-1]
    res = predictor.predict(latest_row)
    return res

@router.post("/run")
async def run_prediction_now():
    return await get_latest_prediction()
