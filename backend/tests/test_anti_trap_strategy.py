import pytest
import datetime
import pandas as pd
import numpy as np
from app.market.schemas import Quote, Candle
from app.features.technical import calculate_anti_trap_features
from app.features.pipeline import build_feature_dataframe
from app.trading.anti_trap_strategy import SmartMoneyAntiTrapEngine
from app.trading.signals import SignalEngine

def test_anti_trap_feature_calculation():
    # Generate 30 sample candles
    dates = pd.date_range("2026-01-01 09:15", periods=30, freq="5min")
    candles = []
    base_price = 24000.0
    for i, d in enumerate(dates):
        candles.append(Candle(
            timestamp=d.isoformat(),
            symbol="NIFTY 50",
            open=base_price + i,
            high=base_price + i + 10,
            low=base_price + i - 5,
            close=base_price + i + 5,
            volume=1000 + i * 100
        ))

    df = build_feature_dataframe(candles)

    assert "swing_high_20" in df.columns
    assert "swing_low_20" in df.columns
    assert "upper_wick_ratio" in df.columns
    assert "lower_wick_ratio" in df.columns
    assert "volume_absorption" in df.columns
    assert "bull_trap_score" in df.columns
    assert "bear_trap_score" in df.columns
    assert len(df) == 30

def test_bull_trap_signal_detection():
    quote = Quote(
        symbol="NIFTY 50",
        last_price=24520.0,
        open=24500.0,
        high=24560.0,  # Sweeps swing high (24530)
        low=24495.0,
        close=24505.0, # Closes low with long upper wick
        volume=50000,
        change=5.0,
        p_change=0.02,
        timestamp="2026-01-01T10:00:00"
    )

    feature_row = {
        "bull_trap_score": 0.85,
        "bear_trap_score": 0.10,
        "upper_wick_ratio": 0.65,
        "lower_wick_ratio": 0.10,
        "volume_absorption": 2.5,
        "swing_high_20": 24530.0,
        "swing_low_20": 24450.0,
        "atr_14": 20.0
    }

    anti_trap_res = SmartMoneyAntiTrapEngine.evaluate_anti_trap_signal(quote, feature_row)

    assert anti_trap_res["signal"] == "SELL"
    assert anti_trap_res["trap_type"] == "BULL_TRAP"
    assert anti_trap_res["confidence"] >= 0.70
    assert anti_trap_res["stop_loss"] > quote.high  # Stop loss set above sweep peak
    assert anti_trap_res["target"] < quote.close   # Target set below entry

def test_bear_trap_signal_detection():
    quote = Quote(
        symbol="NIFTY 50",
        last_price=24405.0,
        open=24420.0,
        high=24430.0,
        low=24370.0,   # Sweeps swing low (24390)
        close=24425.0, # Closes high with long lower wick
        volume=50000,
        change=-15.0,
        p_change=-0.06,
        timestamp="2026-01-01T10:00:00"
    )

    feature_row = {
        "bull_trap_score": 0.10,
        "bear_trap_score": 0.85,
        "upper_wick_ratio": 0.10,
        "lower_wick_ratio": 0.65,
        "volume_absorption": 2.5,
        "swing_high_20": 24480.0,
        "swing_low_20": 24390.0,
        "atr_14": 20.0
    }

    anti_trap_res = SmartMoneyAntiTrapEngine.evaluate_anti_trap_signal(quote, feature_row)

    assert anti_trap_res["signal"] == "BUY"
    assert anti_trap_res["trap_type"] == "BEAR_TRAP"
    assert anti_trap_res["confidence"] >= 0.70
    assert anti_trap_res["stop_loss"] < quote.low  # Stop loss set below sweep bottom
    assert anti_trap_res["target"] > quote.close   # Target set above entry

def test_signal_engine_integration_anti_trap():
    quote = Quote(
        symbol="NIFTY 50",
        last_price=24520.0,
        open=24500.0,
        high=24560.0,
        low=24495.0,
        close=24505.0,
        volume=50000,
        change=5.0,
        p_change=0.02,
        timestamp=datetime.datetime.utcnow().isoformat()
    )

    feature_row = {
        "bull_trap_score": 0.85,
        "bear_trap_score": 0.10,
        "upper_wick_ratio": 0.65,
        "lower_wick_ratio": 0.10,
        "volume_absorption": 2.5,
        "swing_high_20": 24530.0,
        "swing_low_20": 24450.0,
        "atr_14": 20.0
    }

    eval_res = SignalEngine.evaluate_signal(
        quote=quote,
        feature_row=feature_row,
        account_equity=100000.0,
        daily_pnl=0.0,
        open_positions_count=0,
        is_trading_paused=False,
        strategy_mode="SMART_MONEY_ANTI_TRAP"
    )

    assert eval_res["signal"] == "SELL"
    assert "ANTI_TRAP" in eval_res["strategy_used"]
    assert eval_res["is_trade_allowed"] is True
    assert eval_res["suggested_quantity"] > 0
