import datetime
from typing import Dict, Any
from app.market.schemas import Quote
from app.ml.predictor import predictor
from app.trading.risk import RiskEngine

class SignalEngine:
    @staticmethod
    def evaluate_signal(
        quote: Quote,
        feature_row: Any,
        account_equity: float,
        daily_pnl: float,
        open_positions_count: int,
        is_trading_paused: bool = False
    ) -> Dict[str, Any]:
        """
        Evaluate full trading signal:
        1. Run ML prediction
        2. Validate data freshness & risk limits
        3. Determine target and stop-loss levels
        4. Return trade actionable payload
        """
        prediction = predictor.predict(feature_row)

        signal = prediction["signal"]
        confidence = prediction["confidence"]
        expected_return = prediction["expected_return"]

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
        stop_loss = 0.0
        target = 0.0

        if signal == "BUY":
            stop_loss = round(entry_price * 0.995, 2)  # 0.5% Stop Loss
            target = round(entry_price * 1.010, 2)     # 1.0% Target
        elif signal == "SELL":
            stop_loss = round(entry_price * 1.005, 2)  # 0.5% Stop Loss
            target = round(entry_price * 0.990, 2)     # 1.0% Target

        position_quantity = 0.0
        if is_valid and signal in ["BUY", "SELL"]:
            position_quantity = RiskEngine.calculate_position_size(
                account_equity=account_equity,
                entry_price=entry_price,
                stop_loss_price=stop_loss
            )

        return {
            "prediction": prediction,
            "signal": signal,
            "confidence": confidence,
            "expected_return": expected_return,
            "entry_price": entry_price,
            "stop_loss": stop_loss,
            "target": target,
            "suggested_quantity": position_quantity,
            "is_trade_allowed": is_valid,
            "risk_status": risk_reason,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
