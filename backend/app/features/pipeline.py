import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from app.market.schemas import Candle
from app.features.technical import (
    calculate_returns,
    calculate_ranges_and_volatility,
    calculate_moving_averages,
    calculate_rsi,
    calculate_macd,
    calculate_atr,
    calculate_bollinger_bands,
    calculate_volume_features
)

FEATURE_COLUMNS = [
    'return_1', 'return_3', 'return_5', 'return_10', 'return_20',
    'high_low_range', 'close_open_range', 'gap_percentage', 'rolling_volatility',
    'ema_9', 'ema_20', 'ema_50', 'sma_20', 'sma_50',
    'rsi_14', 'macd', 'macd_signal', 'macd_hist',
    'atr_14', 'bollinger_upper', 'bollinger_lower', 'bollinger_width',
    'volume_change', 'rolling_volume', 'volume_ratio'
]

def build_feature_dataframe(candles: List[Candle]) -> pd.DataFrame:
    """Build technical feature dataframe from Candle objects in strict chronological order."""
    if not candles:
        return pd.DataFrame()

    data = []
    for c in candles:
        data.append({
            'timestamp': c.timestamp,
            'symbol': c.symbol,
            'open': c.open,
            'high': c.high,
            'low': c.low,
            'close': c.close,
            'volume': c.volume
        })

    df = pd.DataFrame(data)
    df = df.sort_values(by='timestamp').reset_index(drop=True)

    df = calculate_returns(df)
    df = calculate_ranges_and_volatility(df)
    df = calculate_moving_averages(df)
    df = calculate_rsi(df)
    df = calculate_macd(df)
    df = calculate_atr(df)
    df = calculate_bollinger_bands(df)
    df = calculate_volume_features(df)

    return df

def generate_classification_targets(
    df: pd.DataFrame,
    horizon_candles: int = 3,  # 3 * 5m = 15 minute horizon
    threshold: float = 0.0001
) -> pd.DataFrame:
    """
    Generate target labels for ML:
    BUY  (1) if future_return > quantile(66%)
    SELL (-1) if future_return < quantile(33%)
    HOLD (0) otherwise
    """
    df = df.copy()
    future_price = df['close'].shift(-horizon_candles)
    future_return = (future_price - df['close']) / df['close']
    df['future_return'] = future_return

    std_dev = future_return.std()
    high_cutoff = max(threshold, std_dev * 0.5)
    low_cutoff = min(-threshold, -std_dev * 0.5)

    conditions = [
        future_return > high_cutoff,
        future_return < low_cutoff
    ]
    choices = [1, -1]  # 1: BUY, -1: SELL, 0: HOLD
    df['target'] = np.select(conditions, choices, default=0)
    
    return df

def prepare_train_test_sets(
    df: pd.DataFrame,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split data chronologically into train, validation, and test sets.
    Strictly NO random splitting to prevent data leakage in time series.
    """
    clean_df = df.dropna(subset=FEATURE_COLUMNS + ['target']).copy()
    n = len(clean_df)

    train_end = int(n * train_ratio)
    val_end = int(n * (train_ratio + val_ratio))

    train_df = clean_df.iloc[:train_end]
    val_df = clean_df.iloc[train_end:val_end]
    test_df = clean_df.iloc[val_end:]

    return train_df, val_df, test_df
