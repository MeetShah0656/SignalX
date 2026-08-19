import datetime
import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    paper_accounts = relationship("PaperAccount", back_populates="user")

class PaperAccount(Base):
    __tablename__ = "paper_accounts"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    initial_balance = Column(Float, default=100000.0)
    cash_balance = Column(Float, default=100000.0)
    equity = Column(Float, default=100000.0)
    realized_pnl = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)
    daily_pnl = Column(Float, default=0.0)
    total_pnl = Column(Float, default=0.0)
    is_trading_paused = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="paper_accounts")
    positions = relationship("Position", back_populates="account")
    orders = relationship("Order", back_populates="account")
    trades = relationship("Trade", back_populates="account")

class MarketData(Base):
    __tablename__ = "market_data"

    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, index=True, nullable=False)
    symbol = Column(String, index=True, nullable=False)
    timeframe = Column(String, default="5m")
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    bid = Column(Float, nullable=True)
    ask = Column(Float, nullable=True)
    vwap = Column(Float, nullable=True)
    oi = Column(Float, nullable=True)
    india_vix = Column(Float, nullable=True)

class Feature(Base):
    __tablename__ = "features"

    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, index=True, nullable=False)
    symbol = Column(String, index=True, nullable=False)
    timeframe = Column(String, default="5m")
    feature_data = Column(JSON, nullable=False)

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, index=True, nullable=False)
    symbol = Column(String, index=True, nullable=False)
    signal = Column(String, nullable=False)  # BUY, SELL, HOLD
    buy_probability = Column(Float, nullable=False)
    sell_probability = Column(Float, nullable=False)
    hold_probability = Column(Float, nullable=False)
    expected_return = Column(Float, nullable=False)
    prediction_horizon_minutes = Column(Integer, default=15)
    model_name = Column(String, nullable=False)
    model_version = Column(String, nullable=False)

class Order(Base):
    __tablename__ = "orders"

    id = Column(String, primary_key=True, default=generate_uuid)
    account_id = Column(String, ForeignKey("paper_accounts.id"), nullable=False)
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # BUY, SELL
    order_type = Column(String, default="MARKET")
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    slippage = Column(Float, default=0.0)
    status = Column(String, default="EXECUTED")  # PENDING, EXECUTED, CANCELLED, REJECTED
    reject_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    account = relationship("PaperAccount", back_populates="orders")

class Position(Base):
    __tablename__ = "positions"

    id = Column(String, primary_key=True, default=generate_uuid)
    account_id = Column(String, ForeignKey("paper_accounts.id"), nullable=False)
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)  # LONG, SHORT
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    entry_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    stop_loss = Column(Float, nullable=False)
    target = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    unrealized_pnl = Column(Float, default=0.0)
    status = Column(String, default="OPEN")  # OPEN, CLOSED
    exit_price = Column(Float, nullable=True)
    exit_timestamp = Column(DateTime, nullable=True)
    exit_reason = Column(String, nullable=True)

    account = relationship("PaperAccount", back_populates="positions")

class Trade(Base):
    __tablename__ = "trades"

    id = Column(String, primary_key=True, default=generate_uuid)
    account_id = Column(String, ForeignKey("paper_accounts.id"), nullable=False)
    position_id = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    side = Column(String, nullable=False)
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=False)
    entry_timestamp = Column(DateTime, nullable=False)
    exit_timestamp = Column(DateTime, nullable=False)
    pnl = Column(Float, nullable=False)
    pnl_percent = Column(Float, nullable=False)
    transaction_cost = Column(Float, default=0.0)
    slippage_cost = Column(Float, default=0.0)
    net_pnl = Column(Float, nullable=False)
    duration_seconds = Column(Float, nullable=False)
    exit_reason = Column(String, nullable=False)
    signal = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    model_version = Column(String, nullable=False)

    account = relationship("PaperAccount", back_populates="trades")

class DailyPerformance(Base):
    __tablename__ = "daily_performance"

    id = Column(String, primary_key=True, default=generate_uuid)
    date = Column(String, index=True, nullable=False)
    starting_balance = Column(Float, nullable=False)
    ending_balance = Column(Float, nullable=False)
    realized_pnl = Column(Float, nullable=False)
    trades_count = Column(Integer, default=0)
    win_count = Column(Integer, default=0)
    loss_count = Column(Integer, default=0)

class MLModelRecord(Base):
    __tablename__ = "models"

    id = Column(String, primary_key=True, default=generate_uuid)
    model_name = Column(String, nullable=False)
    model_version = Column(String, unique=True, nullable=False)
    model_type = Column(String, nullable=False)  # XGBoost, RandomForest, LogisticRegression
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_active = Column(Boolean, default=False)
    features_list = Column(JSON, nullable=False)
    metrics = Column(JSON, nullable=False)  # accuracy, precision, recall, f1, backtest_pnl, etc.
    parameters = Column(JSON, nullable=False)
    filepath = Column(String, nullable=False)

class BacktestRun(Base):
    __tablename__ = "backtests"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    start_date = Column(String, nullable=False)
    end_date = Column(String, nullable=False)
    timeframe = Column(String, default="5m")
    model_version = Column(String, nullable=False)
    initial_capital = Column(Float, nullable=False)
    final_equity = Column(Float, nullable=False)
    total_return = Column(Float, nullable=False)
    win_rate = Column(Float, nullable=False)
    profit_factor = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    sharpe_ratio = Column(Float, nullable=False)
    sortino_ratio = Column(Float, nullable=False)
    trades_count = Column(Integer, nullable=False)
    equity_curve = Column(JSON, nullable=False)
    parameters = Column(JSON, nullable=False)

class SystemEvent(Base):
    __tablename__ = "system_events"

    id = Column(String, primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    event_type = Column(String, nullable=False)  # INFO, WARN, ERROR, TRADING_SIGNAL, ORDER_EXECUTION
    component = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
