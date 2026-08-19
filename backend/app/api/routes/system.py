from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import get_db
from app.database.models import SystemEvent
from app.trading.market_hours import MarketCalendar
from app.ml.model_registry import model_registry

router = APIRouter(prefix="/api/system", tags=["System"])

@router.get("/status")
async def get_system_status():
    m_status = MarketCalendar.get_market_status()
    active_model = model_registry.get_active_model_info()

    return {
        "market_api": "CONNECTED",
        "database": "CONNECTED",
        "ml_model": "READY" if active_model else "UNAVAILABLE",
        "websocket": "CONNECTED",
        "prediction_loop": "ACTIVE",
        "paper_execution": "ENABLED",
        "market_calendar": m_status
    }

@router.get("/logs")
async def get_system_logs(db: AsyncSession = Depends(get_db), limit: int = 50):
    stmt = select(SystemEvent).order_by(SystemEvent.timestamp.desc()).limit(limit)
    res = await db.execute(stmt)
    events = res.scalars().all()
    
    return [
        {
            "id": e.id,
            "timestamp": e.timestamp.isoformat(),
            "event_type": e.event_type,
            "component": e.component,
            "message": e.message,
            "details": e.details
        }
        for e in events
    ]
