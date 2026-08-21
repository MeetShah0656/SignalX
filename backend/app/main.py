import asyncio
import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.core.config import settings
from app.core.logging import logger
from app.core.security import setup_security
from app.database.database import init_db, AsyncSessionLocal
from app.api.routes import health, market, prediction, trading, portfolio, backtest, model, analytics, system
from app.api.websocket import ws_manager
from app.market.factory import get_market_provider
from app.trading.portfolio import get_or_create_paper_account
from app.trading.position_manager import PositionManager

from app.features.pipeline import build_feature_dataframe
from app.trading.signals import SignalEngine

bg_task = None

async def live_data_loop():
    """Background task streaming live quote updates, automated paper trading, and position monitoring via WebSocket."""
    logger.info("Starting live market data background stream loop...")
    provider = get_market_provider()

    while True:
        try:
            quote = await provider.get_latest_quote("NIFTY 50")
            
            # Broadcast latest market quote
            await ws_manager.broadcast("market_update", quote.dict())

            # Update active paper positions live (and check 10m auto-expiry)
            async with AsyncSessionLocal() as db:
                account = await get_or_create_paper_account(db)
                pos_manager = PositionManager(db)
                open_positions = await pos_manager.update_active_positions(quote, account)

                # Continuous Automated Paper Trading Loop
                if settings.AUTO_TRADING_ENABLED and len(open_positions) < settings.MAX_OPEN_POSITIONS:
                    candles = await provider.get_historical_candles("NIFTY 50", timeframe="5m", limit=100)
                    if len(candles) >= 30:
                        df_features = build_feature_dataframe(candles)
                        if not df_features.empty:
                            latest_row = df_features.iloc[-1]
                            eval_res = SignalEngine.evaluate_signal(
                                quote=quote,
                                feature_row=latest_row,
                                account_equity=account.equity,
                                daily_pnl=account.daily_pnl,
                                open_positions_count=len(open_positions),
                                is_trading_paused=False,
                                strategy_mode=settings.DEFAULT_TRADING_STRATEGY
                            )
                            if eval_res["is_trade_allowed"] and eval_res["signal"] in ["BUY", "SELL"]:
                                trade_res = await pos_manager.open_position(
                                    account=account,
                                    quote=quote,
                                    signal=eval_res["signal"],
                                    confidence=eval_res["confidence"],
                                    model_version=eval_res["prediction"].get("model_version", "v1"),
                                    stop_loss=eval_res["stop_loss"],
                                    target=eval_res["target"],
                                    quantity=eval_res["suggested_quantity"]
                                )
                                logger.info(f"Auto Trading Bot opened {eval_res['signal']} position on NIFTY 50 (10m Max Duration)")
                                await ws_manager.broadcast("trade_update", trade_res)

                await ws_manager.broadcast("portfolio_update", {
                    "equity": account.equity,
                    "cash_balance": account.cash_balance,
                    "unrealized_pnl": account.unrealized_pnl,
                    "realized_pnl": account.realized_pnl,
                    "open_positions": open_positions,
                    "auto_trading_enabled": settings.AUTO_TRADING_ENABLED
                })

        except Exception as e:
            logger.error(f"Error in background market loop: {e}")

        await asyncio.sleep(3)  # Broadcast quote every 3 seconds

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing SignalX AI NIFTY Live Paper Trading Backend...")
    await init_db()
    global bg_task
    bg_task = asyncio.create_task(live_data_loop())
    yield
    # Shutdown actions
    logger.info("Shutting down SignalX backend...")
    if bg_task:
        bg_task.cancel()

app = FastAPI(
    title="SignalX - AI NIFTY Live Paper Trading API",
    description="Production-grade AI NIFTY 50 paper trading engine and backtesting platform.",
    version="1.0.0",
    lifespan=lifespan
)

# Setup CORS
setup_security(app)

# Include Routers
app.include_router(health.router)
app.include_router(market.router)
app.include_router(prediction.router)
app.include_router(trading.router)
app.include_router(portfolio.router)
app.include_router(backtest.router)
app.include_router(model.router)
app.include_router(analytics.router)
app.include_router(system.router)

@app.websocket("/ws/market")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection open and listen for ping/messages
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
