from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.database.database import get_db
from app.database.models import PaperAccount, Trade, Position, Order
from app.trading.portfolio import get_or_create_paper_account, calculate_account_metrics
from app.core.config import settings

router = APIRouter(prefix="/api/portfolio", tags=["Portfolio"])

@router.get("")
async def get_portfolio(db: AsyncSession = Depends(get_db)):
    account = await get_or_create_paper_account(db)
    metrics = await calculate_account_metrics(db, account)
    return metrics

@router.get("/performance")
async def get_performance(db: AsyncSession = Depends(get_db)):
    account = await get_or_create_paper_account(db)
    stmt = select(Trade).where(Trade.account_id == account.id).order_by(Trade.exit_timestamp.asc())
    res = await db.execute(stmt)
    trades = res.scalars().all()

    equity_curve = [{"timestamp": account.created_at.isoformat(), "equity": account.initial_balance}]
    running_equity = account.initial_balance

    for t in trades:
        running_equity += t.net_pnl
        equity_curve.append({
            "timestamp": t.exit_timestamp.isoformat(),
            "equity": round(running_equity, 2)
        })

    return {
        "account_id": account.id,
        "initial_balance": account.initial_balance,
        "current_equity": account.equity,
        "total_pnl": account.total_pnl,
        "total_trades": len(trades),
        "equity_curve": equity_curve
    }

@router.post("/reset")
async def reset_paper_account(db: AsyncSession = Depends(get_db)):
    account = await get_or_create_paper_account(db)

    # Delete orders, positions, trades associated with this account
    await db.execute(delete(Position).where(Position.account_id == account.id))
    await db.execute(delete(Order).where(Order.account_id == account.id))
    await db.execute(delete(Trade).where(Trade.account_id == account.id))

    account.initial_balance = settings.INITIAL_CAPITAL
    account.cash_balance = settings.INITIAL_CAPITAL
    account.equity = settings.INITIAL_CAPITAL
    account.realized_pnl = 0.0
    account.unrealized_pnl = 0.0
    account.daily_pnl = 0.0
    account.total_pnl = 0.0
    account.is_trading_paused = False

    await db.commit()
    await db.refresh(account)

    return {
        "success": True,
        "message": "Paper account reset to initial capital ₹100,000.",
        "account": await calculate_account_metrics(db, account)
    }
