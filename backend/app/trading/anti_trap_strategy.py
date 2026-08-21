import datetime
import numpy as np
from typing import Dict, Any
from app.market.schemas import Quote

class SmartMoneyAntiTrapEngine:
    """
    Quantitative Anti-Retail / Smart Money Engine.
    Detects institutional liquidity sweeps, fake breakouts (bull traps),
    and panic breakdown traps (bear traps) to counter-trade retail patterns.
    """

    @staticmethod
    def evaluate_anti_trap_signal(quote: Quote, feature_row: Any) -> Dict[str, Any]:
        """
        Evaluate anti-trap signals:
        - Detect Bull Traps -> Initiate Counter-SELL (Short)
        - Detect Bear Traps -> Initiate Counter-BUY (Long)
        - Returns signal, confidence, stop_loss, target, and anti_trap_metadata
        """
        def get_val(key: str, default: float = 0.0) -> float:
            if hasattr(feature_row, "get"):
                val = feature_row.get(key, default)
                if val is not None and not (isinstance(val, float) and np.isnan(val)):
                    return float(val)
                return default
            elif hasattr(feature_row, key):
                val = getattr(feature_row, key)
                if val is not None:
                    return float(val)
                return default
            return default

        bull_trap_score = get_val("bull_trap_score", 0.0)
        bear_trap_score = get_val("bear_trap_score", 0.0)
        upper_wick_ratio = get_val("upper_wick_ratio", 0.0)
        lower_wick_ratio = get_val("lower_wick_ratio", 0.0)
        volume_absorption = get_val("volume_absorption", 1.0)
        swing_high = get_val("swing_high_20", quote.close + 15.0)
        swing_low = get_val("swing_low_20", quote.close - 15.0)
        atr = max(15.0, get_val("atr_14", 20.0))

        entry_price = quote.close

        # Thresholds for anti-retail counter-trading
        BULL_TRAP_THRESHOLD = 0.55
        BEAR_TRAP_THRESHOLD = 0.55

        signal = "HOLD"
        confidence = 0.0
        stop_loss = 0.0
        target = 0.0
        trap_type = "NONE"
        message = "No market trap pattern detected. Standard equilibrium."

        if bull_trap_score >= BULL_TRAP_THRESHOLD:
            # Market Runners trapped retail buyers above key high/resistance
            signal = "SELL"
            trap_type = "BULL_TRAP"
            confidence = min(0.95, round(0.68 + (bull_trap_score - BULL_TRAP_THRESHOLD) * 0.5, 4))
            
            # Place Stop Loss safely above the liquidity sweep peak (+5 points cushion)
            sweep_peak = max(quote.high, swing_high)
            stop_loss = round(sweep_peak + 5.0, 2)
            
            # Target initial mean-reversion level / opposing liquidity zone (~1.8x ATR)
            target_distance = max(30.0, round(atr * 1.8, 2))
            target = round(entry_price - target_distance, 2)
            
            message = (f"BULL TRAP DETECTED (Score: {bull_trap_score:.2f}). "
                       f"Retail buyers trapped above {swing_high:.2f} with {upper_wick_ratio*100:.0f}% upper wick rejection. "
                       f"Counter-SELL paper trade activated.")

        elif bear_trap_score >= BEAR_TRAP_THRESHOLD:
            # Market Runners trapped retail panic sellers below key low/support
            signal = "BUY"
            trap_type = "BEAR_TRAP"
            confidence = min(0.95, round(0.68 + (bear_trap_score - BEAR_TRAP_THRESHOLD) * 0.5, 4))

            # Place Stop Loss safely below the liquidity sweep bottom (-5 points cushion)
            sweep_bottom = min(quote.low, swing_low)
            stop_loss = round(sweep_bottom - 5.0, 2)

            # Target initial squeeze / opposing liquidity zone (~1.8x ATR)
            target_distance = max(30.0, round(atr * 1.8, 2))
            target = round(entry_price + target_distance, 2)

            message = (f"BEAR TRAP DETECTED (Score: {bear_trap_score:.2f}). "
                       f"Retail panic sellers trapped below {swing_low:.2f} with {lower_wick_ratio*100:.0f}% lower wick rejection. "
                       f"Counter-BUY paper trade activated.")

        return {
            "signal": signal,
            "confidence": confidence,
            "trap_type": trap_type,
            "bull_trap_score": round(bull_trap_score, 4),
            "bear_trap_score": round(bear_trap_score, 4),
            "upper_wick_ratio": round(upper_wick_ratio, 4),
            "lower_wick_ratio": round(lower_wick_ratio, 4),
            "volume_absorption": round(volume_absorption, 4),
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "target": target,
            "message": message,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
