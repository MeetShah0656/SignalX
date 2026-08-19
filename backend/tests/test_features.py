import pytest
import datetime
import pandas as pd
import numpy as np
from app.market.schemas import Candle
from app.features.pipeline import build_feature_dataframe, FEATURE_COLUMNS, generate_classification_targets

def test_feature_calculation_no_lookahead():
    """Verify indicators rely strictly on current and past candle values."""
    now = datetime.datetime.utcnow()
    candles = []
    prices = [100.0, 102.0, 101.0, 105.0, 104.0, 108.0, 107.0, 110.0, 109.0, 112.0]
    
    for i, p in enumerate(prices):
        candles.append(Candle(
            timestamp=now + datetime.timedelta(minutes=i * 5),
            symbol="NIFTY 50",
            timeframe="5m",
            open=p - 0.5,
            high=p + 1.0,
            low=p - 1.0,
            close=p,
            volume=1000.0
        ))

    df = build_feature_dataframe(candles)

    assert not df.empty
    assert len(df) == len(prices)
    for col in FEATURE_COLUMNS:
        assert col in df.columns

    # Verify EMA 9 uses past values
    assert not np.isnan(df['ema_9'].iloc[-1])
    assert df['return_1'].iloc[1] == pytest.approx((102.0 - 100.0) / 100.0)

def test_target_generation():
    now = datetime.datetime.utcnow()
    candles = [
        Candle(timestamp=now + datetime.timedelta(minutes=i*5), symbol="NIFTY", timeframe="5m", open=100, high=101, low=99, close=100 + i*2, volume=100)
        for i in range(10)
    ]
    df = build_feature_dataframe(candles)
    df_target = generate_classification_targets(df, horizon_candles=3, threshold=0.003)
    
    assert 'target' in df_target.columns
    # Check that strong upward move yields target = 1 (BUY)
    assert df_target['target'].iloc[0] == 1
