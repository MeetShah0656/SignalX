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
from app.market.live_provider import LiveMarketDataProvider
from app.market.mock_provider import MockMarketDataProvider
from app.trading.portfolio import get_or_create_paper_account
from app.trading.position_manager import PositionManager

bg_task = None

def get_provider():
    if settings.MARKET_DATA_PROVIDER == "live" or settings.MARKET_DATA_PROVIDER == "yfinance":
        return LiveMarketDataProvider(settings.SYMBOL)
    return MockMarketDataProvider()

async def live_data_loop():
    """Background task streaming live quote updates and position monitoring via WebSocket."""
    logger.info("Starting live market data background stream loop...")
    provider = get_provider()

    while True:
        try:
            quote = await provider.get_latest_quote("NIFTY 50")
            
            # Broadcast latest market quote
            await ws_manager.broadcast("market_update", quote.dict())

            # Update active paper positions live
            async with AsyncSessionLocal() as db:
                account = await get_or_create_paper_account(db)
                pos_manager = PositionManager(db)
                open_positions = await pos_manager.update_active_positions(quote, account)
                
                await ws_manager.broadcast("portfolio_update", {
                    "equity": account.equity,
                    "cash_balance": account.cash_balance,
                    "unrealized_pnl": account.unrealized_pnl,
                    "realized_pnl": account.realized_pnl,
                    "open_positions": open_positions
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
