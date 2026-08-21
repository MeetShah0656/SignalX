from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional
import datetime
import uuid
from app.database.database import get_db
from app.database.models import BacktestRun
from app.market.factory import get_market_provider
from app.backtesting.engine import BacktestEngine
from app.core.config import settings

router = APIRouter(prefix="/api/backtest", tags=["Backtesting"])

@router.post("")
async def run_backtest(
    payload: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    timeframe = payload.get("timeframe", "5m")
    initial_capital = float(payload.get("initial_capital", settings.INITIAL_CAPITAL))
    buy_threshold = float(payload.get("buy_threshold", settings.BUY_THRESHOLD))
    sell_threshold = float(payload.get("sell_threshold", settings.SELL_THRESHOLD))
    stop_loss_pct = float(payload.get("stop_loss_pct", 0.005))
    target_pct = float(payload.get("target_pct", 0.010))

    provider = get_market_provider()
    candles = await provider.get_historical_candles("NIFTY 50", timeframe=timeframe, limit=500)

    if len(candles) < 30:
        raise HTTPException(status_code=400, detail="Insufficient historical candles for backtesting.")

    engine = BacktestEngine(initial_capital=initial_capital)
    res = engine.run_backtest(
        candles=candles,
        buy_threshold=buy_threshold,
        sell_threshold=sell_threshold,
        stop_loss_pct=stop_loss_pct,
        target_pct=target_pct
    )

    metrics = res["metrics"]
    backtest_id = str(uuid.uuid4())
    now_str = datetime.datetime.utcnow().strftime("%Y-%m-%d")

    db_backtest = BacktestRun(
        id=backtest_id,
        name=f"Backtest NIFTY {timeframe} - {now_str}",
        start_date=candles[0].timestamp.isoformat(),
        end_date=candles[-1].timestamp.isoformat(),
        timeframe=timeframe,
        model_version="xgb_v1",
        initial_capital=initial_capital,
        final_equity=metrics["final_equity"],
        total_return=metrics["total_return"],
        win_rate=metrics["win_rate"],
        profit_factor=metrics["profit_factor"],
        max_drawdown=metrics["max_drawdown"],
        sharpe_ratio=metrics["sharpe_ratio"],
        sortino_ratio=metrics["sortino_ratio"],
        trades_count=metrics["total_trades"],
        equity_curve=res["equity_curve"],
        parameters=payload
    )
    db.add(db_backtest)
    await db.commit()

    return {
        "id": backtest_id,
        "metrics": metrics,
        "equity_curve": res["equity_curve"],
        "trades": res["trades"]
    }

@router.get("/{backtest_id}")
async def get_backtest(backtest_id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(BacktestRun).where(BacktestRun.id == backtest_id)
    res = await db.execute(stmt)
    bt = res.scalars().first()
    if not bt:
        raise HTTPException(status_code=404, detail="Backtest run not found.")

    return {
        "id": bt.id,
        "name": bt.name,
        "created_at": bt.created_at.isoformat(),
        "timeframe": bt.timeframe,
        "metrics": {
            "initial_capital": bt.initial_capital,
            "final_equity": bt.final_equity,
            "total_return": bt.total_return,
            "win_rate": bt.win_rate,
            "profit_factor": bt.profit_factor,
            "max_drawdown": bt.max_drawdown,
            "sharpe_ratio": bt.sharpe_ratio,
            "sortino_ratio": bt.sortino_ratio,
            "total_trades": bt.trades_count
        },
        "equity_curve": bt.equity_curve,
        "parameters": bt.parameters
    }
