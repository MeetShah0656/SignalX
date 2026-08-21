from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import get_db
from app.database.models import Position, Trade, PaperAccount
from app.market.factory import get_market_provider
from app.features.pipeline import build_feature_dataframe
from app.trading.signals import SignalEngine
from app.trading.position_manager import PositionManager
from app.trading.portfolio import get_or_create_paper_account
from app.api.websocket import ws_manager
from app.core.config import settings

router = APIRouter(prefix="/api/trading", tags=["Paper Trading"])

@router.post("/start")
async def start_paper_trade(db: AsyncSession = Depends(get_db)):
    account = await get_or_create_paper_account(db)
    provider = get_market_provider()

    quote = await provider.get_latest_quote("NIFTY 50")
    candles = await provider.get_historical_candles("NIFTY 50", timeframe="5m", limit=100)
    df_features = build_feature_dataframe(candles)

    if df_features.empty or len(df_features) < 20:
        raise HTTPException(status_code=400, detail="Insufficient market candles to calculate feature pipeline.")

    latest_row = df_features.iloc[-1]

    # Get open positions count
    stmt = select(Position).where(Position.account_id == account.id, Position.status == "OPEN")
    res = await db.execute(stmt)
    open_positions = res.scalars().all()

    eval_res = SignalEngine.evaluate_signal(
        quote=quote,
        feature_row=latest_row,
        account_equity=account.equity,
        daily_pnl=account.daily_pnl,
        open_positions_count=len(open_positions),
        is_trading_paused=account.is_trading_paused
    )

    if not eval_res["is_trade_allowed"]:
        return {
            "success": False,
            "status": "REJECTED",
            "reason": eval_res["risk_status"],
            "signal": eval_res["signal"],
            "confidence": eval_res["confidence"],
            "quote": quote.dict()
        }

    pos_manager = PositionManager(db)
    trade_res = await pos_manager.open_position(
        account=account,
        quote=quote,
        signal=eval_res["signal"],
        confidence=eval_res["confidence"],
        model_version=eval_res["prediction"].get("model_version", "v1"),
        stop_loss=eval_res["stop_loss"],
        target=eval_res["target"],
        quantity=eval_res["suggested_quantity"]
    )

    # Broadcast websocket event
    await ws_manager.broadcast("trade_update", trade_res)

    return trade_res

@router.post("/close")
async def close_position(position_id: str, db: AsyncSession = Depends(get_db)):
    account = await get_or_create_paper_account(db)
    stmt = select(Position).where(Position.id == position_id, Position.account_id == account.id, Position.status == "OPEN")
    res = await db.execute(stmt)
    pos = res.scalars().first()

    if not pos:
        raise HTTPException(status_code=404, detail="Open position not found.")

    provider = get_market_provider()
    quote = await provider.get_latest_quote(pos.symbol)

    pos_manager = PositionManager(db)
    close_res = await pos_manager.close_position(pos, account, quote, exit_reason="MANUAL_EXIT")
    
    await ws_manager.broadcast("trade_update", close_res)
    return close_res

@router.get("/positions")
async def get_positions(db: AsyncSession = Depends(get_db)):
    account = await get_or_create_paper_account(db)
    provider = get_market_provider()
    quote = await provider.get_latest_quote("NIFTY 50")

    pos_manager = PositionManager(db)
    open_positions = await pos_manager.update_active_positions(quote, account)
    return open_positions

@router.get("/trades")
async def get_trades(db: AsyncSession = Depends(get_db), limit: int = 100):
    account = await get_or_create_paper_account(db)
    stmt = select(Trade).where(Trade.account_id == account.id).order_by(Trade.exit_timestamp.desc()).limit(limit)
    res = await db.execute(stmt)
    trades = res.scalars().all()
    
    return [
        {
            "trade_id": t.id,
            "position_id": t.position_id,
            "symbol": t.symbol,
            "side": t.side,
            "quantity": t.quantity,
            "entry_price": t.entry_price,
            "exit_price": t.exit_price,
            "entry_timestamp": t.entry_timestamp.isoformat(),
            "exit_timestamp": t.exit_timestamp.isoformat(),
            "gross_pnl": t.pnl,
            "net_pnl": t.net_pnl,
            "pnl_percent": t.pnl_percent,
            "duration_seconds": t.duration_seconds,
            "exit_reason": t.exit_reason,
            "model_version": t.model_version
        }
        for t in trades
    ]

@router.post("/pause")
async def pause_trading(db: AsyncSession = Depends(get_db)):
    account = await get_or_create_paper_account(db)
    account.is_trading_paused = True
    await db.commit()
    return {"status": "PAUSED", "is_trading_paused": True}

@router.post("/resume")
async def resume_trading(db: AsyncSession = Depends(get_db)):
    account = await get_or_create_paper_account(db)
    account.is_trading_paused = False
    await db.commit()
    return {"status": "ACTIVE", "is_trading_paused": False}

@router.post("/toggle-auto")
async def toggle_auto_trading():
    settings.AUTO_TRADING_ENABLED = not settings.AUTO_TRADING_ENABLED
    return {
        "auto_trading_enabled": settings.AUTO_TRADING_ENABLED,
        "message": f"Automated Trading Bot {'ENABLED' if settings.AUTO_TRADING_ENABLED else 'DISABLED'}. (10-minute max position limit active)."
    }

@router.delete("/trades/{trade_id}")
async def delete_single_trade(trade_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Trade).where(Trade.id == trade_id)
    res = await db.execute(stmt)
    trade = res.scalar_one_or_none()
    if not trade:
        return {"status": "ERROR", "message": "Trade not found"}
    
    account = await get_or_create_paper_account(db)
    account.cash_balance -= trade.net_pnl
    account.equity -= trade.net_pnl
    account.realized_pnl -= trade.net_pnl
    account.total_pnl -= trade.net_pnl

    await db.delete(trade)
    await db.commit()
    return {"status": "SUCCESS", "message": f"Trade {trade_id} deleted."}
