import datetime
from typing import Dict, Any
from app.market.schemas import Quote
from app.ml.predictor import predictor
from app.trading.risk import RiskEngine
from app.trading.anti_trap_strategy import SmartMoneyAntiTrapEngine

class SignalEngine:
    @staticmethod
    def evaluate_signal(
        quote: Quote,
        feature_row: Any,
        account_equity: float,
        daily_pnl: float,
        open_positions_count: int,
        is_trading_paused: bool = False,
        strategy_mode: str = "SMART_MONEY_ANTI_TRAP"
    ) -> Dict[str, Any]:
        """
        Evaluate full trading signal:
        1. Evaluate Anti-Trap / Smart Money signal (detecting market runner traps)
        2. Evaluate standard ML model prediction
        3. Determine final trade signal, target, and stop-loss levels based on strategy_mode
        4. Validate risk constraints & position size
        """
        prediction = predictor.predict(feature_row)
        anti_trap_res = SmartMoneyAntiTrapEngine.evaluate_anti_trap_signal(quote, feature_row)

        signal = "HOLD"
        confidence = 0.0
        expected_return = 0.0
        stop_loss = 0.0
        target = 0.0
        strategy_used = strategy_mode

        atr = float(feature_row.get("atr_14", 20.0)) if hasattr(feature_row, "get") else 20.0

        if strategy_mode in ["SMART_MONEY_ANTI_TRAP", "HYBRID"]:
            if anti_trap_res["signal"] in ["BUY", "SELL"]:
                signal = anti_trap_res["signal"]
                confidence = anti_trap_res["confidence"]
                stop_loss = anti_trap_res["stop_loss"]
                target = anti_trap_res["target"]
                expected_return = 0.005 if signal == "BUY" else -0.005
                strategy_used = f"ANTI_TRAP ({anti_trap_res['trap_type']})"
            elif strategy_mode == "HYBRID":
                # Fallback to ML prediction if no trap pattern is active
                signal = prediction["signal"]
                confidence = prediction["confidence"]
                expected_return = prediction["expected_return"]
                strategy_used = "STANDARD_AI"
            else:
                # Anti-Trap standalone mode with no trap active
                signal = "HOLD"
                confidence = anti_trap_res["confidence"]
                strategy_used = "ANTI_TRAP (MONITORING)"

        if signal in ["BUY", "SELL"] and stop_loss == 0.0:
            entry_price = quote.close
            target_offset = max(25.0, round(atr * 1.5, 2))
            stop_loss_offset = max(15.0, round(atr * 0.8, 2))
            if signal == "BUY":
                target = round(entry_price + target_offset, 2)
                stop_loss = round(entry_price - stop_loss_offset, 2)
            else:
                target = round(entry_price - target_offset, 2)
                stop_loss = round(entry_price + stop_loss_offset, 2)

        # Run Risk Checks
        is_valid, risk_reason = RiskEngine.validate_trade_request(
            quote=quote,
            signal=signal,
            confidence=confidence,
            current_equity=account_equity,
            daily_pnl=daily_pnl,
            open_positions_count=open_positions_count,
            is_trading_paused=is_trading_paused
        )

        entry_price = quote.close
        position_quantity = 0.0
        if is_valid and signal in ["BUY", "SELL"]:
            position_quantity = RiskEngine.calculate_position_size(
                account_equity=account_equity,
                entry_price=entry_price,
                stop_loss_price=stop_loss
            )

        distance = abs(target - entry_price) if target > 0 else 0.0
        estimated_time = max(5, min(30, int(round((distance / max(1.0, atr)) * 5))))

        return {
            "prediction": prediction,
            "anti_trap": anti_trap_res,
            "strategy_mode": strategy_mode,
            "strategy_used": strategy_used,
            "signal": signal,
            "confidence": confidence,
            "expected_return": expected_return,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "target": target,
            "estimated_time_minutes": estimated_time,
            "suggested_quantity": position_quantity,
            "is_trade_allowed": is_valid,
            "risk_status": risk_reason,
            "message": anti_trap_res["message"] if anti_trap_res["signal"] in ["BUY", "SELL"] else "Signal evaluated successfully.",
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

