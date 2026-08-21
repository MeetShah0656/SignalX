import pytest
import datetime
from app.market.schemas import Quote
from app.trading.risk import RiskEngine

def test_risk_validation_passed():
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

    is_valid, reason = RiskEngine.validate_trade_request(
        quote=quote,
        signal="BUY",
        confidence=0.75,
        current_equity=100000.0,
        daily_pnl=0.0,
        open_positions_count=0,
        is_trading_paused=False
    )

    assert is_valid is True
    assert reason == "RISK_CHECK_PASSED"

def test_risk_validation_kill_switch():
    quote = Quote(
        symbol="NIFTY 50",
        timestamp=datetime.datetime.utcnow(),
        open=24600.0, high=24700.0, low=24580.0, close=24685.0, volume=10000.0
    )
    is_valid, reason = RiskEngine.validate_trade_request(
        quote=quote, signal="BUY", confidence=0.80, current_equity=100000.0, daily_pnl=0.0, open_positions_count=0, is_trading_paused=True
    )
    assert is_valid is False
    assert "TRADING_PAUSED" in reason

def test_position_sizing_calculation():
    qty = RiskEngine.calculate_position_size(
        account_equity=100000.0,
        entry_price=24685.40,
        stop_loss_price=24612.10
    )
    assert qty == 50.0  # 2 Lots (2 * 25 = 50.0 shares)
