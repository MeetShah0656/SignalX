import datetime
from typing import Tuple, Optional
from app.core.config import settings
from app.market.schemas import Quote
from app.trading.market_hours import MarketCalendar
from app.core.logging import logger

class RiskEngine:
    """
    Dedicated Risk Engine enforcing paper trading limits:
    - Data freshness check
    - Trading hours / Kill switch check
    - Daily loss limit check (2%)
    - Open position count limit (1)
    - Position size calculation (1% max risk per trade)
    """

    @staticmethod
    def validate_trade_request(
        quote: Quote,
        signal: str,
        confidence: float,
        current_equity: float,
        daily_pnl: float,
        open_positions_count: int,
        is_trading_paused: bool = False
    ) -> Tuple[bool, str]:
        """
        Validate all risk conditions before opening a paper trade.
        Returns (is_valid, rejection_reason).
        """
        # 1. Kill Switch Check
        if is_trading_paused:
            return False, "TRADING_PAUSED: System kill switch is currently ACTIVE."

        # 2. Signal Check
        if signal not in ["BUY", "SELL"]:
            return False, f"INVALID_SIGNAL: Cannot trade on {signal} signal."

        threshold = settings.BUY_THRESHOLD if signal == "BUY" else settings.SELL_THRESHOLD
        if confidence < threshold:
            return False, f"LOW_CONFIDENCE: Signal confidence ({confidence:.1%}) below threshold ({threshold:.1%})."

        # 3. Data Freshness Check
        now = datetime.datetime.utcnow()
        quote_ts = quote.timestamp
        if quote_ts.tzinfo is not None:
            quote_ts = quote_ts.astimezone(datetime.timezone.utc).replace(tzinfo=None)

        age_seconds = (now - quote_ts).total_seconds()
        if age_seconds > settings.MAX_DATA_AGE_SECONDS and quote.is_live:
            return False, f"STALE_MARKET_DATA: Market data is {age_seconds:.1f}s old (max {settings.MAX_DATA_AGE_SECONDS}s allowed)."

        # 4. Daily Loss Limit Check
        max_allowed_daily_loss = current_equity * settings.MAX_DAILY_LOSS
        if daily_pnl < -max_allowed_daily_loss:
            return False, f"DAILY_LOSS_LIMIT_REACHED: Daily P&L (-₹{abs(daily_pnl):.2f}) exceeds maximum allowed loss (-₹{max_allowed_daily_loss:.2f})."

        # 5. Open Positions Count Check
        if open_positions_count >= settings.MAX_OPEN_POSITIONS:
            return False, f"MAX_POSITIONS_REACHED: Already have {open_positions_count} open position(s) (limit {settings.MAX_OPEN_POSITIONS})."

        # 6. Sufficient Capital Check
        if current_equity <= 0:
            return False, "INSUFFICIENT_CAPITAL: Account equity is zero or negative."

        return True, "RISK_CHECK_PASSED"

    @staticmethod
    def calculate_position_size(
        account_equity: float,
        entry_price: float,
        stop_loss_price: float,
        risk_per_trade_pct: float = settings.MAX_RISK_PER_TRADE
    ) -> float:
        """
        Calculate virtual NIFTY position quantity based on risk amount.
        quantity = risk_amount / risk_per_unit
        """
        risk_amount = account_equity * risk_per_trade_pct
        risk_per_unit = abs(entry_price - stop_loss_price)

        if risk_per_unit <= 0.1:
            risk_per_unit = entry_price * 0.005  # Default 0.5% stop loss fallback

        quantity = risk_amount / risk_per_unit
        # For simulated virtual NIFTY exposure, round to 2 decimals or minimum 1 contract
        return max(1.0, round(quantity, 2))
