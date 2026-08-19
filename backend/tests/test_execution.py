import pytest
import datetime
from app.market.schemas import Quote
from app.trading.paper_execution import PaperExecutionEngine

@pytest.mark.asyncio
async def test_paper_execution_buy_slippage():
    quote = Quote(
        symbol="NIFTY 50",
        timestamp=datetime.datetime.utcnow(),
        open=24600.0,
        high=24700.0,
        low=24580.0,
        close=24685.0,
        volume=10000.0,
        bid=24684.50,
        ask=24685.50
    )

    engine = PaperExecutionEngine(slippage_bps=5.0)
    order_res = await engine.execute_order("NIFTY 50", "BUY", 1.0, quote)

    assert order_res["status"] == "EXECUTED"
    assert order_res["execution_price"] > 24685.50  # Ask price + slippage
    assert order_res["execution_type"] == "SIMULATED_PAPER_ORDER"

@pytest.mark.asyncio
async def test_paper_execution_sell_slippage():
    quote = Quote(
        symbol="NIFTY 50",
        timestamp=datetime.datetime.utcnow(),
        open=24600.0,
        high=24700.0,
        low=24580.0,
        close=24685.0,
        volume=10000.0,
        bid=24684.50,
        ask=24685.50
    )

    engine = PaperExecutionEngine(slippage_bps=5.0)
    order_res = await engine.execute_order("NIFTY 50", "SELL", 1.0, quote)

    assert order_res["status"] == "EXECUTED"
    assert order_res["execution_price"] < 24684.50  # Bid price - slippage
