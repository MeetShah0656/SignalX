from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database.database import get_db
from app.ml.model_registry import model_registry
from app.core.config import settings

router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    db_status = "disconnected"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "error"

    active_model = model_registry.get_active_model_info()
    model_status = "ready" if active_model else "not_trained"

    return {
        "status": "healthy",
        "database": db_status,
        "market_data": "connected",
        "market_data_provider": settings.MARKET_DATA_PROVIDER,
        "model": model_status,
        "active_model_version": active_model.get("model_version") if active_model else None,
        "paper_trading": "enabled"
    }
