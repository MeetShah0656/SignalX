import pandas as pd
import numpy as np

def calculate_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate historical price returns without lookahead bias."""
    df['return_1'] = df['close'].pct_change(1)
    df['return_3'] = df['close'].pct_change(3)
    df['return_5'] = df['close'].pct_change(5)
    df['return_10'] = df['close'].pct_change(10)
    df['return_20'] = df['close'].pct_change(20)
    return df

def calculate_ranges_and_volatility(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate price ranges and rolling volatility."""
    df['high_low_range'] = (df['high'] - df['low']) / df['close']
    df['close_open_range'] = (df['close'] - df['open']) / df['open']
    df['gap_percentage'] = (df['open'] - df['close'].shift(1)) / df['close'].shift(1)
    df['rolling_volatility'] = df['return_1'].rolling(window=20).std()
    return df

def calculate_moving_averages(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate EMA and SMA technical indicators."""
    df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
    df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
    
    df['sma_20'] = df['close'].rolling(window=20).mean()
    df['sma_50'] = df['close'].rolling(window=50).mean()
    return df

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Calculate Relative Strength Index (RSI)."""
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / (loss + 1e-9)
    df['rsi_14'] = 100 - (100 / (1 + rs))
    return df

def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """Calculate MACD line, signal line, and histogram."""
    exp1 = df['close'].ewm(span=fast, adjust=False).mean()
    exp2 = df['close'].ewm(span=slow, adjust=False).mean()
    macd = exp1 - exp2
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    
    df['macd'] = macd
    df['macd_signal'] = signal_line
    df['macd_hist'] = macd - signal_line
    return df

def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """Calculate Average True Range (ATR)."""
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift(1)).abs()
    low_close = (df['low'] - df['close'].shift(1)).abs()
    
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr_14'] = tr.rolling(window=period).mean()
    return df

def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, num_std: float = 2.0) -> pd.DataFrame:
    """Calculate Bollinger Bands and bandwidth."""
    sma = df['close'].rolling(window=period).mean()
    std = df['close'].rolling(window=period).std()
    
    df['bollinger_upper'] = sma + (std * num_std)
    df['bollinger_lower'] = sma - (std * num_std)
    df['bollinger_width'] = (df['bollinger_upper'] - df['bollinger_lower']) / (sma + 1e-9)
    return df

def calculate_volume_features(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate volume features."""
    df['volume_change'] = df['volume'].pct_change(1)
    df['rolling_volume'] = df['volume'].rolling(window=20).mean()
    df['volume_ratio'] = df['volume'] / (df['rolling_volume'] + 1e-9)
    return df

def calculate_anti_trap_features(df: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """
    Calculate Smart Money & Anti-Retail Liquidity Trap features:
    - Swing Highs / Lows (Key retail liquidity levels)
    - Upper & Lower Wick Ratios (Pinbar / Rejection detection)
    - Volume Absorption (Institutional distribution/accumulation trapping retail)
    - Bull Trap & Bear Trap composite scores
    """
    # Key retail liquidity boundaries (excluding current candle to prevent lookahead)
    df['swing_high_20'] = df['high'].shift(1).rolling(window=window).max()
    df['swing_low_20'] = df['low'].shift(1).rolling(window=window).min()

    candle_range = df['high'] - df['low'] + 1e-9
    real_body = (df['close'] - df['open']).abs()

    df['upper_wick_ratio'] = (df['high'] - df[['open', 'close']].max(axis=1)) / candle_range
    df['lower_wick_ratio'] = (df[['open', 'close']].min(axis=1) - df['low']) / candle_range

    # Volume Absorption: High relative volume relative to net price spread (real body)
    body_pct = (real_body / df['close']) + 1e-4
    df['volume_absorption'] = df['volume_ratio'] / (body_pct * 100)

    # Bull Trap indicator score (0.0 to 1.0)
    # Triggers when price probes above recent swing high / upper bollinger band but rejected downwards
    probed_high = df['high'] >= df['swing_high_20']
    rejected_down = df['close'] < df['open']
    high_upper_wick = df['upper_wick_ratio'] > 0.4
    vol_absorbed = df['volume_absorption'] > 1.2

    bull_trap = (probed_high.astype(int) * 0.35 +
                 rejected_down.astype(int) * 0.25 +
                 high_upper_wick.astype(int) * 0.25 +
                 vol_absorbed.astype(int) * 0.15)
    df['bull_trap_score'] = bull_trap

    # Bear Trap indicator score (0.0 to 1.0)
    # Triggers when price probes below recent swing low / lower bollinger band but rejected upwards
    probed_low = df['low'] <= df['swing_low_20']
    rejected_up = df['close'] > df['open']
    high_lower_wick = df['lower_wick_ratio'] > 0.4

    bear_trap = (probed_low.astype(int) * 0.35 +
                 rejected_up.astype(int) * 0.25 +
                 high_lower_wick.astype(int) * 0.25 +
                 vol_absorbed.astype(int) * 0.15)
    df['bear_trap_score'] = bear_trap

    return df

