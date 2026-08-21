from fastapi import APIRouter, Depends, Query
from typing import Optional
from app.market.factory import get_market_provider
from app.features.pipeline import build_feature_dataframe, FEATURE_COLUMNS
from app.ml.predictor import predictor
from app.trading.signals import SignalEngine
from app.core.config import settings

router = APIRouter(prefix="/api/prediction", tags=["Predictions"])

@router.get("/latest")
async def get_latest_prediction(strategy_mode: Optional[str] = Query(None)):
    provider = get_market_provider()
    quote = await provider.get_latest_quote("NIFTY 50")
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
    strat = strategy_mode or settings.DEFAULT_TRADING_STRATEGY
    
    eval_res = SignalEngine.evaluate_signal(
        quote=quote,
        feature_row=latest_row,
        account_equity=100000.0,
        daily_pnl=0.0,
        open_positions_count=0,
        is_trading_paused=False,
        strategy_mode=strat
    )
    return eval_res

@router.post("/run")
async def run_prediction_now(strategy_mode: Optional[str] = Query(None)):
    return await get_latest_prediction(strategy_mode=strategy_mode)
