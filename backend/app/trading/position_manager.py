import datetime
import uuid
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database.models import Position, Order, Trade, PaperAccount, SystemEvent
from app.market.schemas import Quote
from app.trading.paper_execution import PaperExecutionEngine
from app.core.logging import logger

class PositionManager:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.execution_engine = PaperExecutionEngine()

    async def open_position(
        self,
        account: PaperAccount,
        quote: Quote,
        signal: str,
        confidence: float,
        model_version: str,
        stop_loss: float,
        target: float,
        quantity: float
    ) -> Dict[str, Any]:
        """Open a new virtual paper position."""
        side = "LONG" if signal == "BUY" else "SHORT"
        order_side = "BUY" if side == "LONG" else "SELL"

        # Execute simulated order
        order_res = await self.execution_engine.execute_order(
            symbol=quote.symbol,
            side=order_side,
            quantity=quantity,
            quote=quote
        )

        entry_price = order_res["execution_price"]

        # Record Order in DB
        db_order = Order(
            id=order_res["order_id"],
            account_id=account.id,
            symbol=quote.symbol,
            side=order_side,
            order_type="MARKET",
            quantity=quantity,
            price=entry_price,
            slippage=order_res["slippage"],
            status="EXECUTED",
            created_at=datetime.datetime.utcnow()
        )
        self.db.add(db_order)

        # Record Position in DB
        position_id = str(uuid.uuid4())
        db_position = Position(
            id=position_id,
            account_id=account.id,
            symbol=quote.symbol,
            side=side,
            quantity=quantity,
            entry_price=entry_price,
            entry_timestamp=datetime.datetime.utcnow(),
            stop_loss=stop_loss,
            target=target,
            current_price=entry_price,
            unrealized_pnl=0.0,
            status="OPEN"
        )
        self.db.add(db_position)

        # Log system event
        event = SystemEvent(
            event_type="ORDER_EXECUTION",
            component="PositionManager",
            message=f"Paper Position Opened: {side} {quantity} units @ ₹{entry_price:.2f} (SL: ₹{stop_loss:.2f}, TP: ₹{target:.2f})",
            details=order_res
        )
        self.db.add(event)

        await self.db.commit()
        await self.db.refresh(db_position)

        return {
            "success": True,
            "trade_id": position_id,
            "position_id": position_id,
            "signal": signal,
            "confidence": confidence,
            "side": side,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "target": target,
            "quantity": quantity,
            "timestamp": db_position.entry_timestamp.isoformat()
        }

    async def update_active_positions(self, quote: Quote, account: PaperAccount) -> List[Dict[str, Any]]:
        """
        Update unrealized P&L for open positions and check exit triggers (SL, TP, etc.).
        """
        stmt = select(Position).where(Position.account_id == account.id, Position.status == "OPEN")
        result = await self.db.execute(stmt)
        open_positions = result.scalars().all()

        updated_positions = []
        current_price = quote.close

        for pos in open_positions:
            # Calculate Unrealized P&L
            if pos.side == "LONG":
                unrealized_pnl = (current_price - pos.entry_price) * pos.quantity
            else:  # SHORT
                unrealized_pnl = (pos.entry_price - current_price) * pos.quantity

            pos.current_price = current_price
            pos.unrealized_pnl = round(unrealized_pnl, 2)

            # Check exit conditions
            exit_reason = None
            if pos.side == "LONG":
                if current_price <= pos.stop_loss:
                    exit_reason = "STOP_LOSS"
                elif current_price >= pos.target:
                    exit_reason = "TARGET_HIT"
            elif pos.side == "SHORT":
                if current_price >= pos.stop_loss:
                    exit_reason = "STOP_LOSS"
                elif current_price <= pos.target:
                    exit_reason = "TARGET_HIT"

            if exit_reason:
                await self.close_position(pos, account, quote, exit_reason)
            else:
                updated_positions.append({
                    "position_id": pos.id,
                    "symbol": pos.symbol,
                    "side": pos.side,
                    "quantity": pos.quantity,
                    "entry_price": pos.entry_price,
                    "current_price": current_price,
                    "stop_loss": pos.stop_loss,
                    "target": pos.target,
                    "unrealized_pnl": pos.unrealized_pnl,
                    "entry_timestamp": pos.entry_timestamp.isoformat()
                })

        await self.db.commit()
        return updated_positions

    async def close_position(
        self,
        position: Position,
        account: PaperAccount,
        quote: Quote,
        exit_reason: str
    ) -> Dict[str, Any]:
        """Close an active position and record trade history and P&L."""
        close_side = "SELL" if position.side == "LONG" else "BUY"
        order_res = await self.execution_engine.execute_order(
            symbol=quote.symbol,
            side=close_side,
            quantity=position.quantity,
            quote=quote
        )

        exit_price = order_res["execution_price"]
        exit_time = datetime.datetime.utcnow()

        # Calculate Realized P&L
        if position.side == "LONG":
            gross_pnl = (exit_price - position.entry_price) * position.quantity
        else:
            gross_pnl = (position.entry_price - exit_price) * position.quantity

        slippage_cost = order_res["slippage"] * position.quantity
        transaction_cost = gross_pnl * 0.0003  # 0.03% estimated transaction fee/STT
        net_pnl = gross_pnl - transaction_cost

        pnl_percent = (net_pnl / (position.entry_price * position.quantity)) * 100.0 if position.entry_price > 0 else 0.0

        # Update position record
        position.status = "CLOSED"
        position.exit_price = exit_price
        position.exit_timestamp = exit_time
        position.exit_reason = exit_reason
        position.unrealized_pnl = 0.0

        # Update Paper Account Balances
        account.cash_balance += net_pnl
        account.realized_pnl += net_pnl
        account.total_pnl += net_pnl
        account.equity = account.cash_balance

        duration_sec = (exit_time - position.entry_timestamp).total_seconds()

        # Create Trade record
        trade_id = str(uuid.uuid4())
        db_trade = Trade(
            id=trade_id,
            account_id=account.id,
            position_id=position.id,
            symbol=position.symbol,
            side=position.side,
            quantity=position.quantity,
            entry_price=position.entry_price,
            exit_price=exit_price,
            entry_timestamp=position.entry_timestamp,
            exit_timestamp=exit_time,
            pnl=round(gross_pnl, 2),
            pnl_percent=round(pnl_percent, 2),
            transaction_cost=round(transaction_cost, 2),
            slippage_cost=round(slippage_cost, 2),
            net_pnl=round(net_pnl, 2),
            duration_seconds=duration_sec,
            exit_reason=exit_reason,
            signal=position.side,
            confidence=0.75,
            model_version="xgb_v1"
        )
        self.db.add(db_trade)

        # Log system event
        event = SystemEvent(
            event_type="POSITION_CLOSED",
            component="PositionManager",
            message=f"Paper Position Closed: {position.side} @ ₹{exit_price:.2f} | Reason: {exit_reason} | Net P&L: ₹{net_pnl:.2f}",
            details={"trade_id": trade_id, "net_pnl": net_pnl, "exit_reason": exit_reason}
        )
        self.db.add(event)

        await self.db.commit()

        logger.info(f"[POSITION CLOSED] Trade ID: {trade_id} | Net P&L: ₹{net_pnl:.2f} | Reason: {exit_reason}")

        return {
            "success": True,
            "trade_id": trade_id,
            "exit_price": exit_price,
            "net_pnl": net_pnl,
            "pnl_percent": pnl_percent,
            "exit_reason": exit_reason
        }
