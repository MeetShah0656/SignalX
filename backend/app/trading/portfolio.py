from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models import PaperAccount, Position
from app.core.config import settings

async def get_or_create_paper_account(db: AsyncSession) -> PaperAccount:
    """Fetch existing paper account or initialize a new default account on first run."""
    stmt = select(PaperAccount).limit(1)
    result = await db.execute(stmt)
    account = result.scalars().first()

    if not account:
        account = PaperAccount(
            initial_balance=settings.INITIAL_CAPITAL,
            cash_balance=settings.INITIAL_CAPITAL,
            equity=settings.INITIAL_CAPITAL,
            realized_pnl=0.0,
            unrealized_pnl=0.0,
            daily_pnl=0.0,
            total_pnl=0.0,
            is_trading_paused=False
        )
        db.add(account)
        await db.commit()
        await db.refresh(account)

    return account

async def calculate_account_metrics(db: AsyncSession, account: PaperAccount) -> dict:
    """Calculate aggregate equity, total unrealized P&L, and account state."""
    stmt = select(Position).where(Position.account_id == account.id, Position.status == "OPEN")
    result = await db.execute(stmt)
    open_positions = result.scalars().all()

    total_unrealized = sum(p.unrealized_pnl for p in open_positions)
    equity = account.cash_balance + total_unrealized

    account.unrealized_pnl = round(total_unrealized, 2)
    account.equity = round(equity, 2)
    await db.commit()

    return {
        "account_id": account.id,
        "initial_balance": account.initial_balance,
        "cash_balance": account.cash_balance,
        "equity": account.equity,
        "realized_pnl": account.realized_pnl,
        "unrealized_pnl": account.unrealized_pnl,
        "daily_pnl": account.daily_pnl,
        "total_pnl": account.total_pnl,
        "is_trading_paused": account.is_trading_paused,
        "open_positions_count": len(open_positions)
    }
