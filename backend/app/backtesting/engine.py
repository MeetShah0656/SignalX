import datetime
import pandas as pd
from typing import List, Dict, Any
from app.market.schemas import Candle
from app.features.pipeline import build_feature_dataframe, FEATURE_COLUMNS
from app.ml.predictor import predictor
from app.backtesting.metrics import calculate_backtest_metrics
from app.core.config import settings

class BacktestEngine:
    def __init__(
        self,
        initial_capital: float = settings.INITIAL_CAPITAL,
        slippage_bps: float = settings.SLIPPAGE_BPS,
        transaction_fee_pct: float = 0.0003
    ):
        self.initial_capital = initial_capital
        self.slippage_bps = slippage_bps
        self.transaction_fee_pct = transaction_fee_pct

    def run_backtest(
        self,
        candles: List[Candle],
        buy_threshold: float = settings.BUY_THRESHOLD,
        sell_threshold: float = settings.SELL_THRESHOLD,
        stop_loss_pct: float = 0.005,
        target_pct: float = 0.010
    ) -> Dict[str, Any]:
        """
        Run backtest over historical candles reusing exact feature pipeline and execution assumptions.
        """
        if not candles or len(candles) < 30:
            raise ValueError("Insufficient candle data for backtest (minimum 30 candles required).")

        df = build_feature_dataframe(candles)
        df_features = df.dropna(subset=FEATURE_COLUMNS).copy()

        capital = self.initial_capital
        equity_curve = []
        trades = []
        position = None

        for idx, row in df_features.iterrows():
            current_time = row['timestamp']
            close_price = row['close']
            high_price = row['high']
            low_price = row['low']

            # If in position, check exit rules (SL / TP)
            if position:
                side = position['side']
                entry_price = position['entry_price']
                quantity = position['quantity']
                sl = position['stop_loss']
                tp = position['target']

                exit_triggered = False
                exit_price = close_price
                exit_reason = ""

                if side == "LONG":
                    if low_price <= sl:
                        exit_triggered = True
                        exit_price = sl
                        exit_reason = "STOP_LOSS"
                    elif high_price >= tp:
                        exit_triggered = True
                        exit_price = tp
                        exit_reason = "TARGET_HIT"
                elif side == "SHORT":
                    if high_price >= sl:
                        exit_triggered = True
                        exit_price = sl
                        exit_reason = "STOP_LOSS"
                    elif low_price <= tp:
                        exit_triggered = True
                        exit_price = tp
                        exit_reason = "TARGET_HIT"

                if exit_triggered:
                    # Apply slippage on exit
                    slippage = exit_price * (self.slippage_bps / 10000.0)
                    actual_exit = (exit_price - slippage) if side == "LONG" else (exit_price + slippage)

                    gross_pnl = (actual_exit - entry_price) * quantity if side == "LONG" else (entry_price - actual_exit) * quantity
                    fee = gross_pnl * self.transaction_fee_pct
                    net_pnl = gross_pnl - fee

                    capital += net_pnl
                    pnl_pct = (net_pnl / (entry_price * quantity)) * 100.0 if entry_price > 0 else 0.0

                    trades.append({
                        "trade_id": len(trades) + 1,
                        "entry_time": position['entry_time'].isoformat() if hasattr(position['entry_time'], 'isoformat') else str(position['entry_time']),
                        "exit_time": current_time.isoformat() if hasattr(current_time, 'isoformat') else str(current_time),
                        "side": side,
                        "quantity": quantity,
                        "entry_price": round(entry_price, 2),
                        "exit_price": round(actual_exit, 2),
                        "net_pnl": round(net_pnl, 2),
                        "pnl_percent": round(pnl_pct, 2),
                        "exit_reason": exit_reason
                    })
                    position = None

            # If not in position, run prediction for entry
            if not position:
                pred = predictor.predict(row)
                signal = pred["signal"]
                conf = pred["confidence"]

                if signal in ["BUY", "SELL"] and conf >= (buy_threshold if signal == "BUY" else sell_threshold):
                    side = "LONG" if signal == "BUY" else "SHORT"
                    
                    # Entry price with slippage
                    slippage = close_price * (self.slippage_bps / 10000.0)
                    entry_price = (close_price + slippage) if side == "LONG" else (close_price - slippage)
                    
                    sl = round(entry_price * (1 - stop_loss_pct), 2) if side == "LONG" else round(entry_price * (1 + stop_loss_pct), 2)
                    tp = round(entry_price * (1 + target_pct), 2) if side == "LONG" else round(entry_price * (1 - target_pct), 2)
                    
                    # 1% risk allocation
                    risk_amount = capital * settings.MAX_RISK_PER_TRADE
                    risk_per_unit = abs(entry_price - sl)
                    quantity = max(1.0, round(risk_amount / (risk_per_unit + 1e-5), 2))

                    position = {
                        "side": side,
                        "entry_price": entry_price,
                        "entry_time": current_time,
                        "quantity": quantity,
                        "stop_loss": sl,
                        "target": tp
                    }

            equity_curve.append({
                "timestamp": current_time.isoformat() if hasattr(current_time, 'isoformat') else str(current_time),
                "equity": round(capital, 2)
            })

        metrics = calculate_backtest_metrics(trades, self.initial_capital, equity_curve)

        return {
            "metrics": metrics,
            "equity_curve": equity_curve,
            "trades": trades
        }
