import datetime
import zoneinfo

class MarketCalendar:
    TIMEZONE = zoneinfo.ZoneInfo("Asia/Kolkata")

    @classmethod
    def get_market_status(cls, dt: datetime.datetime = None) -> dict:
        if dt is None:
            dt = datetime.datetime.now(cls.TIMEZONE)
        elif dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc).astimezone(cls.TIMEZONE)
        else:
            dt = dt.astimezone(cls.TIMEZONE)

        # Check weekend (5 = Saturday, 6 = Sunday)
        if dt.weekday() >= 5:
            return {
                "is_open": False,
                "status": "MARKET_CLOSED",
                "reason": "WEEKEND",
                "timezone": "Asia/Kolkata",
                "current_time": dt.strftime("%Y-%m-%d %H:%M:%S IST")
            }

        market_open = dt.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = dt.replace(hour=15, minute=30, second=0, microsecond=0)
        pre_open = dt.replace(hour=9, minute=0, second=0, microsecond=0)

        if dt < pre_open:
            status = "MARKET_CLOSED"
            is_open = False
        elif pre_open <= dt < market_open:
            status = "PRE_OPEN"
            is_open = False
        elif market_open <= dt <= market_close:
            status = "MARKET_OPEN"
            is_open = True
        else:
            status = "POST_MARKET"
            is_open = False

        return {
            "is_open": is_open,
            "status": status,
            "timezone": "Asia/Kolkata",
            "current_time": dt.strftime("%Y-%m-%d %H:%M:%S IST")
        }
