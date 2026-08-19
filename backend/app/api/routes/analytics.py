from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.database import get_db
from app.database.models import Trade
from app.trading.portfolio import get_or_create_paper_account
from app.backtesting.metrics import calculate_backtest_metrics

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("")
async def get_analytics(db: AsyncSession = Depends(get_db)):
    account = await get_or_create_paper_account(db)
    stmt = select(Trade).where(Trade.account_id == account.id).order_by(Trade.exit_timestamp.asc())
    res = await db.execute(stmt)
    trades = res.scalars().all()

    trade_list = [
        {
            "net_pnl": t.net_pnl,
            "pnl_percent": t.pnl_percent,
            "exit_reason": t.exit_reason
        }
        for t in trades
    ]

    equity_curve = [{"timestamp": account.created_at.isoformat(), "equity": account.initial_balance}]
    running_eq = account.initial_balance
    for t in trades:
        running_eq += t.net_pnl
        equity_curve.append({
            "timestamp": t.exit_timestamp.isoformat(),
            "equity": round(running_eq, 2)
        })

    metrics = calculate_backtest_metrics(trade_list, account.initial_balance, equity_curve)

    best_trade = max((t.net_pnl for t in trades), default=0.0)
    worst_trade = min((t.net_pnl for t in trades), default=0.0)

    metrics["best_trade"] = round(best_trade, 2)
    metrics["worst_trade"] = round(worst_trade, 2)

    return {
        "metrics": metrics,
        "equity_curve": equity_curve,
        "signal_distribution": {
            "LONG": len([t for t in trades if t.side == "LONG"]),
            "SHORT": len([t for t in trades if t.side == "SHORT"])
        }
    }
