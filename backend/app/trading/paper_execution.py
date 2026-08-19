from abc import ABC, abstractmethod
import datetime
import uuid
from typing import Dict, Any, Tuple
from app.market.schemas import Quote
from app.core.config import settings
from app.core.logging import logger

class ExecutionEngine(ABC):
    @abstractmethod
    async def execute_order(
        self,
        symbol: str,
        side: str,  # BUY or SELL
        quantity: float,
        quote: Quote
    ) -> Dict[str, Any]:
        """
        Execute an order abstract method.
        Note: Actual broker execution is deliberately excluded to ensure absolute safety.
        Only PaperExecutionEngine is implemented in this system.
        """
        pass

class PaperExecutionEngine(ExecutionEngine):
    def __init__(self, slippage_bps: float = settings.SLIPPAGE_BPS):
        self.slippage_bps = slippage_bps

    async def execute_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        quote: Quote
    ) -> Dict[str, Any]:
        """
        Simulate order execution against bid/ask or LTP with configurable slippage.
        BUY orders execute at ask price + slippage.
        SELL orders execute at bid price - slippage.
        """
        ltp = quote.close
        if side == "BUY":
            base_price = quote.ask if quote.ask and quote.ask > 0 else ltp
            slippage_amount = base_price * (self.slippage_bps / 10000.0)
            execution_price = round(base_price + slippage_amount, 2)
        else:
            base_price = quote.bid if quote.bid and quote.bid > 0 else ltp
            slippage_amount = base_price * (self.slippage_bps / 10000.0)
            execution_price = round(base_price - slippage_amount, 2)

        order_id = str(uuid.uuid4())
        timestamp = datetime.datetime.utcnow()

        logger.info(
            f"[PAPER TRADING] Order Executed | Order ID: {order_id} | Side: {side} | "
            f"Qty: {quantity} | Base Price: ₹{base_price:.2f} | Execution Price: ₹{execution_price:.2f} | "
            f"Slippage: {self.slippage_bps} bps (₹{slippage_amount:.2f})"
        )

        return {
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "base_price": base_price,
            "execution_price": execution_price,
            "slippage": round(slippage_amount, 2),
            "slippage_bps": self.slippage_bps,
            "status": "EXECUTED",
            "timestamp": timestamp.isoformat(),
            "execution_type": "SIMULATED_PAPER_ORDER"
        }
