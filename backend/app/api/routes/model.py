from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Dict, Any
from app.ml.model_registry import model_registry
from app.ml.trainer import train_and_evaluate_models
from app.market.factory import get_market_provider
from app.features.pipeline import build_feature_dataframe, generate_classification_targets
from app.core.config import settings

router = APIRouter(prefix="/api/model", tags=["AI Model"])

@router.get("/status")
async def get_model_status():
    info = model_registry.get_active_model_info()
    if not info:
        return {
            "status": "NOT_TRAINED",
            "active_model": None,
            "message": "Model not trained. Run the training pipeline before enabling AI predictions."
        }
    return {
        "status": "READY",
        "active_model": info
    }

@router.get("/metrics")
async def get_model_metrics():
    info = model_registry.get_active_model_info()
    if not info:
        raise HTTPException(status_code=404, detail="Active model metrics not available.")
    return info.get("metrics", {})

@router.post("/train")
async def train_model_pipeline(payload: Dict[str, Any] = Body(default={})):
    limit = payload.get("limit", 500)
    timeframe = payload.get("timeframe", "5m")

    provider = get_market_provider()
    candles = await provider.get_historical_candles("NIFTY 50", timeframe=timeframe, limit=limit)

    if len(candles) < 50:
        raise HTTPException(status_code=400, detail=f"Insufficient candles for training (got {len(candles)}, minimum 50 required).")

    df_features = build_feature_dataframe(candles)
    df_dataset = generate_classification_targets(df_features, horizon_candles=3, threshold=0.003)

    res = train_and_evaluate_models(df_dataset)
    return {
        "success": True,
        "message": f"Successfully trained and registered model {res['model_version']}",
        "result": res
    }
