# AI NIFTY Live Paper Trading System

## 1. PROJECT OBJECTIVE

Build a complete, production-quality **AI-powered live NIFTY paper-trading application** using Python for the backend and a modern web frontend.

The application must:

1. Receive live NSE/NIFTY market data through a legitimate market-data/broker API.
2. Display live NIFTY market information.
3. Calculate technical and market features in real time.
4. Generate live BUY / SELL / HOLD predictions using a machine-learning model.
5. Show prediction confidence and supporting information.
6. Allow the user to click a **START TRADE** button.
7. At that exact point, evaluate the latest available market state and AI prediction.
8. Open a **virtual/paper position only**.
9. Never send real orders to an exchange or broker.
10. Continuously monitor the virtual position.
11. Automatically close positions according to the selected strategy, target, stop-loss, or exit signal.
12. Maintain virtual capital and calculate live P&L.
13. Store every prediction and trade in a database.
14. Provide historical trade analytics.
15. Provide a backtesting engine using historical data.
16. Provide model-performance analytics.
17. Clearly separate live market data, prediction, paper execution, and future broker integration.
18. Be fully runnable locally after setup.
19. Include error handling, logging, configuration management, health checks, and tests.
20. Never claim that the model guarantees profitability.

IMPORTANT:

This is a **paper-trading application only**.

Do NOT implement real-money order execution.

Do NOT connect an order-placement endpoint.

Do NOT automatically place actual NSE orders.

The application must simulate all trades internally.

---

# 2. CORE PRODUCT CONCEPT

The user should be able to open the application and see:

```text
LIVE NIFTY 50
24,685.40
+0.38%

AI SIGNAL
BUY

Confidence
73.4%

Expected Direction
UP

Expected Move
+0.42%

Entry
24,685.40

Target
24,789.20

Stop Loss
24,612.10

[ START PAPER TRADE ]
```

When the user presses:

```text
START PAPER TRADE
```

the backend must:

1. Retrieve the latest available market data.
2. Verify the market-data timestamp.
3. Calculate the current features.
4. Run the ML model.
5. Generate BUY / SELL / HOLD.
6. Verify risk conditions.
7. Record the signal timestamp.
8. Record bid/ask/last traded price if available.
9. Determine a realistic simulated execution price.
10. Open a virtual position.
11. Store the trade in the database.
12. Update the frontend immediately.

Never fabricate a successful trade.

If live market data is unavailable, the system must explicitly show:

```text
MARKET DATA UNAVAILABLE
```

and must NOT create a trade.

---

# 3. IMPORTANT SAFETY / EXECUTION RULES

The system must be paper trading only.

Create an explicit execution abstraction:

```text
MarketDataProvider
PredictionEngine
RiskEngine
PaperExecutionEngine
PortfolioManager
```

The architecture must make it impossible for the current application to accidentally send real orders.

The paper execution engine must be the only execution implementation enabled.

Use an interface such as:

```python
class ExecutionEngine:
    def execute_order(...)
```

and implement:

```python
class PaperExecutionEngine(ExecutionEngine):
    ...
```

Do NOT implement:

```python
class LiveBrokerExecutionEngine
```

in this version.

If broker integration is required in the future, it should be a separate future module.

---

# 4. TECHNOLOGY STACK

## Backend

Use:

- Python 3.12+
- FastAPI
- Pydantic
- SQLAlchemy
- PostgreSQL
- Alembic
- Pandas
- NumPy
- scikit-learn
- XGBoost
- joblib
- httpx
- WebSockets
- pytest
- pytest-asyncio
- APScheduler or equivalent task scheduler

Use type hints throughout the Python codebase.

Use asynchronous programming where appropriate.

---

# 5. FRONTEND

Use:

- Next.js
- TypeScript
- React
- Tailwind CSS
- Recharts or Lightweight Charts
- WebSocket client
- TanStack Query where useful

The frontend must be responsive.

It must work on:

- Desktop
- Laptop
- Tablet
- Mobile

Design should look like a professional trading dashboard rather than a generic admin panel.

---

# 6. APPLICATION STRUCTURE

Create the following high-level structure:

```text
nifty-ai-trader/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── market.py
│   │   │   │   ├── prediction.py
│   │   │   │   ├── trading.py
│   │   │   │   ├── portfolio.py
│   │   │   │   ├── backtest.py
│   │   │   │   ├── analytics.py
│   │   │   │   └── system.py
│   │   │   └── websocket.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logging.py
│   │   │   └── security.py
│   │   │
│   │   ├── database/
│   │   │   ├── database.py
│   │   │   ├── models.py
│   │   │   └── repositories/
│   │   │
│   │   ├── market/
│   │   │   ├── provider.py
│   │   │   ├── live_provider.py
│   │   │   ├── historical_provider.py
│   │   │   └── schemas.py
│   │   │
│   │   ├── features/
│   │   │   ├── technical.py
│   │   │   ├── market.py
│   │   │   └── pipeline.py
│   │   │
│   │   ├── ml/
│   │   │   ├── trainer.py
│   │   │   ├── predictor.py
│   │   │   ├── features.py
│   │   │   ├── evaluation.py
│   │   │   └── model_registry.py
│   │   │
│   │   ├── trading/
│   │   │   ├── signals.py
│   │   │   ├── risk.py
│   │   │   ├── paper_execution.py
│   │   │   ├── portfolio.py
│   │   │   └── position_manager.py
│   │   │
│   │   ├── backtesting/
│   │   │   ├── engine.py
│   │   │   ├── metrics.py
│   │   │   └── walk_forward.py
│   │   │
│   │   └── services/
│   │       ├── market_service.py
│   │       ├── prediction_service.py
│   │       └── trading_service.py
│   │
│   ├── tests/
│   ├── scripts/
│   │   ├── train_model.py
│   │   ├── download_data.py
│   │   └── run_backtest.py
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   ├── types/
│   ├── public/
│   ├── package.json
│   └── .env.example
│
├── data/
│   ├── historical/
│   ├── models/
│   └── exports/
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

You may improve this structure if necessary, but preserve clean separation of responsibilities.

---

# 7. LIVE MARKET DATA

Create a provider abstraction:

```python
class MarketDataProvider:
    async def get_latest_quote(self, symbol):
        ...

    async def get_historical_data(self, symbol, timeframe):
        ...

    async def subscribe(self, symbols):
        ...
```

The system must support a real API provider through environment variables.

Do NOT hardcode API keys.

Use:

```text
MARKET_DATA_API_KEY=
MARKET_DATA_API_SECRET=
MARKET_DATA_BASE_URL=
```

The provider must be replaceable.

Do not scrape NSE website pages as the primary real-time data mechanism.

If the selected API requires authentication, provide exact setup instructions in README.

---

# 8. MARKET DATA REQUIREMENTS

At minimum capture:

```text
timestamp
symbol
open
high
low
close / LTP
volume
bid
ask
```

If available, also capture:

```text
VWAP
OI
change in OI
India VIX
market breadth
```

Do not assume that every provider supplies every field.

The application must gracefully handle unavailable optional fields.

---

# 9. LIVE DATA TIMEFRAME

The first version should focus on **intraday NIFTY 50 paper trading**.

Support:

```text
1 minute
5 minute
15 minute
```

The default model timeframe should be:

```text
5-minute candles
```

The architecture must allow another timeframe to be selected later.

Do not claim that tick-level prediction is possible unless the chosen data source actually supplies tick-level data.

---

# 10. FEATURE ENGINEERING

Build a feature pipeline.

At minimum calculate:

## Price features

```text
return_1
return_3
return_5
return_10
return_20

high_low_range
close_open_range

gap_percentage
rolling_volatility
```

## Moving averages

```text
EMA 9
EMA 20
EMA 50
SMA 20
SMA 50
```

## Momentum

```text
RSI
MACD
MACD signal
MACD histogram
ROC
```

## Volatility

```text
ATR
Bollinger Bands
Bollinger Band width
```

## Volume

```text
volume_change
volume_ratio
rolling_volume
```

## Market context

If available:

```text
India VIX
Bank Nifty return
NIFTY return
market breadth
```

All feature calculations must be deterministic and unit tested.

Avoid look-ahead bias.

---

# 11. MACHINE LEARNING TARGET

Do NOT train the model simply to predict the exact future NIFTY price.

Instead define classification targets.

For example:

```text
BUY
SELL
HOLD
```

For each historical observation:

```text
future_return = future_price / current_price - 1
```

Use a configurable prediction horizon.

Example:

```text
PREDICTION_HORIZON_MINUTES=15
```

Define thresholds based on realistic transaction costs and configurable strategy parameters.

For example:

```text
BUY:
future return > threshold

SELL:
future return < -threshold

HOLD:
otherwise
```

The threshold must NOT be hardcoded permanently.

Make it configurable.

---

# 12. MACHINE LEARNING MODELS

Implement at least:

```text
Logistic Regression
Random Forest
XGBoost
```

The training system must compare them.

Evaluation must include:

```text
accuracy
precision
recall
F1
ROC-AUC where applicable
confusion matrix
```

But do NOT choose the model based only on classification accuracy.

The trading strategy must also be evaluated.

---

# 13. TRAINING PIPELINE

Create:

```bash
python scripts/train_model.py
```

The training pipeline must:

1. Load historical data.
2. Validate data.
3. Remove duplicates.
4. Sort chronologically.
5. Generate features.
6. Generate labels.
7. Split chronologically.
8. Train models.
9. Evaluate models.
10. Run trading simulation.
11. Select the best model using predefined evaluation criteria.
12. Save model.
13. Save feature metadata.
14. Save training configuration.
15. Save evaluation metrics.

Never use random train/test splitting for time-series data.

Use chronological train/validation/test sets.

---

# 14. WALK-FORWARD VALIDATION

Implement walk-forward validation.

Example:

```text
Training:
2019 → 2022

Validation:
2023

Training:
2019 → 2023

Validation:
2024

Training:
2019 → 2024

Test:
2025
```

Use configurable windows.

The system must prevent future information from leaking into training.

---

# 15. MODEL OUTPUT

The predictor should return something like:

```json
{
  "signal": "BUY",
  "buy_probability": 0.734,
  "sell_probability": 0.162,
  "hold_probability": 0.104,
  "expected_return": 0.0042,
  "prediction_horizon_minutes": 15,
  "model_version": "xgb_v12",
  "timestamp": "..."
}
```

The UI should display:

```text
BUY
73.4%

Expected return:
+0.42%

Prediction horizon:
15 minutes
```

---

# 16. SIGNAL ENGINE

Create a separate signal engine.

Example logic:

```python
if buy_probability >= BUY_THRESHOLD:
    signal = BUY

elif sell_probability >= SELL_THRESHOLD:
    signal = SELL

else:
    signal = HOLD
```

But the signal engine must also consider:

```text
expected return
transaction costs
market status
existing position
risk limits
data freshness
```

A prediction alone must not automatically create a trade.

---

# 17. DATA FRESHNESS

Every live prediction must verify data freshness.

Example:

```text
maximum_data_age_seconds = 10
```

If data is older than the allowed threshold:

```text
NO TRADE
```

Display:

```text
STALE MARKET DATA
```

Do not silently use stale prices.

---

# 18. PAPER TRADING ACCOUNT

On first launch create a virtual account.

Default:

```text
Starting capital:
₹100,000
```

Make this configurable.

Store:

```text
initial_balance
cash_balance
equity
realized_pnl
unrealized_pnl
daily_pnl
total_pnl
```

No actual money is involved.

---

# 19. PAPER ORDER ENGINE

Implement:

```text
Market order
Limit order
Stop-loss
Target
```

At minimum the UI must support market-style paper execution.

Simulated execution should use:

```text
ask price for BUY
bid price for SELL
```

when bid/ask are available.

Otherwise use LTP and mark the execution as an approximation.

Include configurable slippage.

Example:

```text
SLIPPAGE_BPS=5
```

---

# 20. POSITION MANAGEMENT

Store:

```text
position_id
symbol
side
quantity
entry_price
entry_timestamp
stop_loss
target
current_price
unrealized_pnl
status
exit_price
exit_timestamp
exit_reason
```

Supported sides:

```text
LONG
SHORT
```

However, only enable short selling if the paper-trading rules explicitly permit it.

---

# 21. RISK MANAGEMENT

Create a dedicated risk engine.

Default limits:

```text
maximum risk per trade = 1%
maximum daily loss = 2%
maximum open positions = 1
```

All should be configurable.

Before opening a paper position:

```text
Check market data freshness
Check trading hours
Check daily loss
Check existing positions
Check position size
Check stop loss
Check capital
Check duplicate order
```

If any check fails:

```text
TRADE REJECTED
```

with a human-readable reason.

---

# 22. POSITION SIZING

Implement configurable risk-based position sizing.

Conceptually:

```text
risk_amount = account_equity × risk_percentage

risk_per_unit =
entry_price - stop_loss

quantity =
risk_amount / risk_per_unit
```

Round quantity appropriately.

For NIFTY derivatives, do NOT assume a lot size that may change over time.

Make contract/lots configuration dynamic and clearly separated from the NIFTY index prediction system.

The first implementation may paper trade a **virtual NIFTY exposure** rather than actual derivative contracts.

Clearly label this:

```text
SIMULATED NIFTY PAPER POSITION
```

---

# 23. EXIT LOGIC

A position should be closed when:

```text
stop loss reached
target reached
model reversal
maximum holding period reached
market closes
risk limit triggered
manual close button pressed
```

Every exit must have a recorded reason.

Example:

```text
TARGET_HIT
STOP_LOSS
SIGNAL_REVERSAL
TIME_EXIT
MANUAL_EXIT
MARKET_CLOSE
RISK_LIMIT
```

---

# 24. USER INTERFACE

Create these pages.

## Dashboard

Display:

```text
NIFTY price
live change
candlestick chart
volume
AI signal
confidence
prediction horizon
expected return
current position
P&L
paper account balance
```

Main CTA:

```text
START PAPER TRADE
```

Also:

```text
CLOSE POSITION
```

---

# 25. CHART

Create a professional candlestick chart.

Show:

```text
Candles
EMA 9
EMA 20
EMA 50
Volume
Entry marker
Exit marker
Stop-loss line
Target line
```

Allow timeframe:

```text
1m
5m
15m
```

---

# 26. TRADE HISTORY

Create a trade-history page.

Columns:

```text
Trade ID
Date
Time
Signal
Confidence
Entry
Exit
Quantity
P&L
P&L %
Duration
Exit reason
Model version
```

Add filters.

---

# 27. ANALYTICS PAGE

Show:

```text
Total trades
Winning trades
Losing trades
Win rate
Average win
Average loss
Profit factor
Maximum drawdown
Sharpe ratio
Sortino ratio
Total P&L
Average trade
Best trade
Worst trade
```

Add charts:

```text
Equity curve
Daily P&L
Win/loss distribution
Drawdown curve
Signal distribution
```

---

# 28. MODEL ANALYTICS

Display:

```text
Current model
Model version
Training date
Training dataset range
Features used
Validation accuracy
Test accuracy
Precision
Recall
F1
ROC-AUC
Trading performance
```

Also display feature importance for tree-based models.

---

# 29. BACKTESTING

Create a backtesting interface.

Inputs:

```text
Start date
End date
Initial capital
Timeframe
Prediction horizon
Model
Buy threshold
Sell threshold
Stop-loss
Target
Slippage
Transaction cost
```

Output:

```text
Total return
CAGR where applicable
Win rate
Profit factor
Maximum drawdown
Sharpe
Sortino
Number of trades
Average trade
```

Provide an equity curve.

---

# 30. BACKTESTING INTEGRITY

The backtester must use the exact same:

```text
feature pipeline
signal engine
risk engine
paper execution assumptions
```

as live paper trading wherever possible.

Do not create one strategy for backtesting and another strategy for live trading.

The same code path should be reused.

---

# 31. NO LOOK-AHEAD BIAS

This is critical.

The system must never use:

```text
future close
future high
future low
future volume
future indicator values
```

when making a current prediction.

Indicators must only use information available at prediction time.

Add automated tests specifically designed to detect look-ahead leakage.

---

# 32. TRADING HOURS

The application must understand NSE market hours.

Do not hardcode assumptions throughout the application.

Create:

```python
MarketCalendar
```

and centralize market-hours logic.

The application must distinguish:

```text
MARKET_OPEN
MARKET_CLOSED
PRE_OPEN
POST_MARKET
HOLIDAY
```

Use the appropriate India timezone:

```text
Asia/Kolkata
```

---

# 33. DATABASE

Use PostgreSQL.

Create tables for:

```text
users
paper_accounts
market_data
features
predictions
orders
positions
trades
daily_performance
models
backtests
system_events
```

Use migrations through Alembic.

---

# 34. IMPORTANT DATA RETENTION RULE

Do not store unlimited high-frequency data blindly.

Use configurable retention.

Separate:

```text
raw market data
aggregated candles
features
predictions
trade records
```

Trade records should be retained permanently unless the user explicitly deletes them.

---

# 35. API ENDPOINTS

Implement at minimum:

```text
GET /api/health

GET /api/market/nifty
GET /api/market/candles

GET /api/prediction/latest
POST /api/prediction/run

POST /api/trading/start
POST /api/trading/close
GET /api/trading/positions
GET /api/trading/trades

GET /api/portfolio
GET /api/portfolio/performance

POST /api/backtest
GET /api/backtest/{id}

GET /api/model/status
GET /api/model/metrics

WebSocket:
/ws/market
/ws/predictions
/ws/portfolio
```

Use proper Pydantic request/response models.

---

# 36. START TRADE API

The most important endpoint:

```text
POST /api/trading/start
```

The backend workflow should be:

```text
Receive request
       ↓
Check market status
       ↓
Get freshest quote
       ↓
Validate timestamp
       ↓
Build latest candle
       ↓
Calculate features
       ↓
Run prediction
       ↓
Generate signal
       ↓
Risk validation
       ↓
Determine simulated execution price
       ↓
Calculate quantity
       ↓
Create paper order
       ↓
Create position
       ↓
Update account
       ↓
Broadcast WebSocket event
       ↓
Return trade information
```

The response should include:

```json
{
  "success": true,
  "trade_id": "...",
  "signal": "BUY",
  "confidence": 0.734,
  "entry_price": 24685.40,
  "stop_loss": 24612.10,
  "target": 24789.20,
  "quantity": 1,
  "timestamp": "..."
}
```

---

# 37. WEBSOCKET

Use WebSockets for live updates.

The backend should broadcast:

```text
market_update
prediction_update
position_update
portfolio_update
trade_update
system_status
```

The frontend should update without requiring manual page refresh.

---

# 38. ERROR HANDLING

Handle:

```text
API timeout
API rate limit
invalid market data
missing candles
stale data
model missing
database failure
WebSocket disconnect
market closed
invalid order
insufficient virtual capital
duplicate trade
```

Never crash the entire application because one market-data request failed.

Use retries with exponential backoff where appropriate.

---

# 39. LOGGING

Create structured logs.

Example:

```text
INFO  Market data updated
INFO  Prediction generated
INFO  Signal BUY
INFO  Risk check passed
INFO  Paper order created
INFO  Position opened
INFO  Position closed
WARN  Market data stale
ERROR Market data provider unavailable
```

Do not log API secrets.

---

# 40. CONFIGURATION

Create:

```text
.env.example
```

Include:

```text
APP_ENV=development

DATABASE_URL=

MARKET_DATA_PROVIDER=
MARKET_DATA_API_KEY=
MARKET_DATA_API_SECRET=
MARKET_DATA_BASE_URL=

INITIAL_CAPITAL=100000

DEFAULT_TIMEFRAME=5m
PREDICTION_HORIZON_MINUTES=15

BUY_THRESHOLD=0.70
SELL_THRESHOLD=0.70

MAX_RISK_PER_TRADE=0.01
MAX_DAILY_LOSS=0.02

SLIPPAGE_BPS=5
```

Never commit `.env`.

---

# 41. DEMO / DEVELOPMENT MODE

Create a development mode.

However, clearly distinguish:

```text
DEMO DATA
```

from:

```text
LIVE MARKET DATA
```

The application must never pretend that demo data is live.

When using demo mode, display a visible banner:

```text
DEMO MODE — MARKET DATA IS SIMULATED
```

When live data is connected:

```text
LIVE DATA
```

---

# 42. MODEL FALLBACK

If a trained model does not exist:

Do NOT fabricate predictions.

Instead display:

```text
MODEL NOT TRAINED

Run the training pipeline before enabling AI predictions.
```

The system should not generate random BUY/SELL predictions as a fake AI.

---

# 43. PAPER TRADING FALLBACK

If live data is unavailable:

Do not create a paper trade.

Show:

```text
Trading unavailable because live market data is unavailable.
```

---

# 44. SECURITY

Implement:

```text
CORS configuration
environment secrets
input validation
rate limiting where appropriate
secure headers
```

Do not expose API credentials to the frontend.

All external API calls requiring secrets must happen on the backend.

---

# 45. FRONTEND DESIGN

Use a dark professional trading terminal aesthetic.

Suggested structure:

```text
Top navigation
│
├── Dashboard
├── Live Market
├── Paper Trading
├── Trade History
├── Analytics
├── Backtesting
├── AI Model
└── Settings
```

Use cards for:

```text
NIFTY
AI SIGNAL
CONFIDENCE
P&L
ACCOUNT EQUITY
POSITION
```

Use clear visual distinction between:

```text
BUY
SELL
HOLD
```

Do not use excessive animations.

The application should feel fast and serious.

---

# 46. DASHBOARD STATUS INDICATORS

Display:

```text
● LIVE DATA CONNECTED

● AI MODEL READY

● PAPER TRADING ENABLED

● MARKET OPEN
```

If anything fails:

```text
● LIVE DATA DISCONNECTED

● MODEL UNAVAILABLE

● PAPER TRADING PAUSED
```

---

# 47. MANUAL CONTROLS

Provide:

```text
START PAPER TRADE
CLOSE POSITION
PAUSE TRADING
RESUME TRADING
RESET PAPER ACCOUNT
```

Reset must require confirmation.

Never automatically reset the user's paper account.

---

# 48. KILL SWITCH

Create a prominent:

```text
PAUSE TRADING
```

control.

When enabled:

```text
No new paper trades
```

Existing positions may continue to be monitored.

Provide:

```text
CLOSE ALL PAPER POSITIONS
```

with confirmation.

---

# 49. MODEL VERSIONING

Every prediction and trade must store:

```text
model_name
model_version
feature_version
strategy_version
```

This allows us to understand which model generated each trade.

---

# 50. REPRODUCIBILITY

Training must save:

```text
model
feature list
hyperparameters
training dates
validation dates
test dates
random seed
metrics
dataset metadata
```

Use a reproducible random seed.

---

# 51. MODEL REGISTRY

Create a simple local model registry.

Example:

```text
models/
    xgb_v1/
    xgb_v2/
    random_forest_v1/
```

The active model should be configurable.

Store metadata:

```json
{
  "model_version": "xgb_v2",
  "created_at": "...",
  "features": [],
  "training_period": "...",
  "test_period": "...",
  "metrics": {}
}
```

---

# 52. PERFORMANCE REQUIREMENT

The application must NOT declare:

```text
PROFITABLE AI
```

simply because a backtest made money.

Instead show:

```text
Backtest performance
Paper trading performance
Out-of-sample performance
```

separately.

The system must explicitly warn that historical performance does not guarantee future performance.

---

# 53. TESTING

Create automated tests for:

## Unit tests

```text
feature calculations
signal generation
position sizing
risk management
P&L calculation
paper execution
market-hours logic
```

## Integration tests

```text
market data → features → model → signal
signal → risk engine → paper order
paper order → position → portfolio
```

## API tests

Test every API endpoint.

## Backtest tests

Verify:

```text
no future data leakage
correct entry price
correct exit price
correct P&L
correct transaction costs
```

---

# 54. TEST DATA

Create small deterministic datasets for testing.

Do not rely exclusively on live APIs for tests.

Use mocked market-data providers.

Example:

```python
MockMarketDataProvider
```

The production application must use the real provider.

---

# 55. HEALTH CHECK

Implement:

```text
GET /api/health
```

Return:

```json
{
  "status": "healthy",
  "database": "connected",
  "market_data": "connected",
  "model": "ready",
  "paper_trading": "enabled"
}
```

---

# 56. STARTUP BEHAVIOR

When backend starts:

1. Load configuration.
2. Connect to database.
3. Run migrations/check schema.
4. Load active model.
5. Initialize market provider.
6. Initialize paper portfolio.
7. Start background market-data service.
8. Start WebSocket manager.
9. Start position monitoring.
10. Expose health endpoint.

If a critical dependency is missing, provide a clear error.

---

# 57. DOCKER

Provide:

```text
docker-compose.yml
```

with:

```text
backend
frontend
postgres
```

The project should be runnable with:

```bash
docker compose up
```

where practical.

Also provide non-Docker instructions.

---

# 58. README

Create an extremely detailed README containing:

## Installation

```text
Prerequisites
Python
Node.js
PostgreSQL
API account
```

## Configuration

Explain every `.env` variable.

## Market data setup

Explain exactly where the user obtains the required API credentials.

Never invent API credentials or URLs.

If the chosen provider is unavailable, explain how to configure another provider through the provider interface.

## Database setup

## Model training

## Backtesting

## Starting the backend

## Starting the frontend

## Running tests

## Live paper trading

## Troubleshooting

## Architecture

## Safety limitations

---

# 59. FIRST-RUN EXPERIENCE

When the user opens the application for the first time:

Show:

```text
Welcome to NIFTY AI Paper Trader

Mode:
PAPER TRADING

Starting Virtual Capital:
₹100,000

Market Data:
NOT CONFIGURED

AI Model:
NOT TRAINED
```

Provide setup guidance.

Once configured:

```text
LIVE DATA CONNECTED
MODEL READY
PAPER TRADING READY
```

---

# 60. MODEL TRAINING UX

Provide a frontend page where the user can:

```text
Select historical dataset
Select timeframe
Select prediction horizon
Select model
Start training
```

Show progress:

```text
Loading data
██████████

Generating features
██████████████

Training XGBoost
██████████████████

Evaluating
████████████████████
```

Then show:

```text
Training complete

Model:
XGBoost v1

Test accuracy:
XX%

Backtest return:
XX%

Maximum drawdown:
XX%

Trades:
XXX
```

Do not hide poor results.

---

# 61. LIVE PREDICTION LOOP

When market is open:

```text
Receive market data
       ↓
Update candle
       ↓
Calculate features
       ↓
Run model
       ↓
Generate probabilities
       ↓
Generate signal
       ↓
Broadcast to frontend
```

The frequency should be configurable.

Do not unnecessarily run expensive model inference hundreds of times per second.

For the initial 5-minute strategy, prediction should update when a new relevant candle/feature state is available.

---

# 62. BUTTON BEHAVIOR

When user clicks:

```text
START PAPER TRADE
```

disable the button temporarily:

```text
ANALYZING...
```

Then:

```text
GETTING LIVE PRICE...
CALCULATING FEATURES...
RUNNING AI...
CHECKING RISK...
OPENING PAPER POSITION...
```

Finally:

```text
TRADE OPENED
```

If rejected:

```text
TRADE NOT OPENED

Reason:
AI confidence below threshold
```

---

# 63. LIVE P&L

Update unrealized P&L using current market price.

Display:

```text
Entry:
₹24,685.40

Current:
₹24,701.20

Unrealized P&L:
+₹15.80
```

For short positions, calculate correctly.

---

# 64. TRANSACTION COSTS

Make transaction-cost assumptions configurable.

Never report gross backtest performance as the primary result.

Show:

```text
Gross P&L
Transaction costs
Slippage
Net P&L
```

---

# 65. STRATEGY CONFIGURATION

Create a settings page.

Allow configuration of:

```text
Timeframe
Prediction horizon
BUY threshold
SELL threshold
Stop loss
Target
Maximum risk
Maximum daily loss
Slippage
Initial capital
```

Validate every value.

---

# 66. DEFAULT STRATEGY

Use sensible defaults but clearly label them as experimental.

Example:

```text
Timeframe:
5 minutes

Prediction horizon:
15 minutes

BUY threshold:
70%

SELL threshold:
70%

Risk:
1%

Maximum daily loss:
2%
```

These are starting parameters, NOT claims that they are optimal.

---

# 67. BACKTEST VS LIVE SEPARATION

Clearly distinguish:

```text
BACKTEST
PAPER TRADING
LIVE MARKET DATA
```

The application must never confuse simulated historical results with live performance.

---

# 68. DATA QUALITY

Validate incoming data for:

```text
missing timestamps
duplicate timestamps
negative prices
impossible OHLC values
missing candles
out-of-order data
abnormal spikes
```

Flag suspicious data.

Do not blindly feed corrupted data into the model.

---

# 69. OBSERVABILITY

Create a system-status panel showing:

```text
Market API
Database
ML model
WebSocket
Prediction loop
Paper execution
```

Each should have:

```text
CONNECTED
DISCONNECTED
ERROR
```

---

# 70. NO FAKE FUNCTIONALITY

This is extremely important.

Do NOT create buttons that only visually work.

Every button must call a real backend function.

Do NOT use hardcoded fake:

```text
NIFTY price
P&L
prediction
trade result
win rate
```

unless the application is explicitly in DEMO MODE.

If a feature cannot be implemented because an external API requires credentials, clearly show:

```text
CONFIGURATION REQUIRED
```

instead of pretending it works.

---

# 71. PROVIDER ABSTRACTION

Implement the following:

```python
class MarketDataProvider(ABC):
    @abstractmethod
    async def latest_quote(self, symbol):
        pass

    @abstractmethod
    async def historical_candles(self, symbol, timeframe, start, end):
        pass
```

Then create the selected provider implementation.

Keep provider-specific code isolated.

This makes it possible to switch providers later without rewriting the application.

---

# 72. PAPER EXECUTION ABSTRACTION

Implement:

```python
class ExecutionEngine(ABC):
    @abstractmethod
    async def execute(self, order):
        pass
```

Only implement:

```python
PaperExecutionEngine
```

for this project.

Add comments explaining that actual broker execution is intentionally excluded.

---

# 73. CLEAN ARCHITECTURE

Do not put everything into:

```text
main.py
```

Use services and modules.

Avoid circular imports.

Use dependency injection for:

```text
database
market provider
prediction engine
execution engine
```

---

# 74. API DOCUMENTATION

FastAPI should automatically expose:

```text
/docs
/redoc
```

Ensure schemas are descriptive.

---

# 75. FRONTEND ERROR STATES

Every page must have proper states:

```text
Loading
Success
Empty
Error
Disconnected
Market closed
Model unavailable
```

Do not leave blank screens.

---

# 76. MOBILE RESPONSIVENESS

On mobile:

```text
NIFTY
SIGNAL
CONFIDENCE
P&L
START TRADE
```

should remain immediately accessible.

Charts can become vertically stacked.

---

# 77. DATABASE SEEDING

Provide optional development seed data.

Clearly label it:

```text
DEMO DATA
```

Never mix demo trades with real paper trades without explicitly indicating the difference.

---

# 78. FINAL ACCEPTANCE TEST

Before declaring the project complete, run this complete flow:

```text
1. Start PostgreSQL
2. Start backend
3. Start frontend
4. Verify health endpoint
5. Verify database
6. Verify market-data provider
7. Load historical data
8. Train model
9. Evaluate model
10. Run backtest
11. Start live market-data stream
12. Display live NIFTY
13. Generate live prediction
14. Press START PAPER TRADE
15. Verify paper position
16. Verify database record
17. Verify live P&L
18. Trigger target/stop-loss in a test environment
19. Verify position closes
20. Verify P&L
21. Verify trade history
22. Verify analytics
23. Verify WebSocket reconnect
24. Run automated tests
25. Verify no real order endpoint exists
```

Only after these checks should the project be considered complete.

---

# 79. IMPORTANT FINAL SECURITY CHECK

Before completion, search the entire project for:

```text
order placement
place_order
submit_order
buy_order
sell_order
broker order API
```

There must be NO real-money execution implementation.

The project should only contain:

```text
PaperExecutionEngine
```

---

# 80. ANTIGRAVITY EXECUTION INSTRUCTIONS

You are the primary autonomous development agent for this project.

Do not merely generate a plan.

Actually create the complete project.

You must:

1. Inspect the workspace.
2. Create the project structure.
3. Implement backend.
4. Implement frontend.
5. Implement database.
6. Implement ML pipeline.
7. Implement backtester.
8. Implement paper execution.
9. Implement WebSockets.
10. Implement tests.
11. Implement Docker configuration.
12. Implement README.
13. Run the application.
14. Fix errors.
15. Run tests.
16. Perform the acceptance test.
17. Fix all issues found.
18. Do not stop after generating placeholder files.

If a dependency or external API requires credentials that are not available, implement the complete provider interface and configuration flow, then clearly identify the exact credential that the user must supply.

Do not fabricate credentials.

Do not fabricate live market data.

Do not fabricate AI predictions.

Do not fabricate profitability.

---

# 81. DEFINITION OF "DONE"

The project is DONE only when:

```text
[ ] Backend starts successfully
[ ] Frontend starts successfully
[ ] Database connects
[ ] Database migrations work
[ ] API documentation works
[ ] Live market-data provider is implemented
[ ] Market data reaches backend
[ ] Live market data reaches frontend
[ ] Technical indicators calculate correctly
[ ] ML training works
[ ] Model saves successfully
[ ] Model loads successfully
[ ] Predictions work
[ ] BUY/SELL/HOLD works
[ ] Risk engine works
[ ] Paper execution works
[ ] Paper positions work
[ ] P&L works
[ ] Stop-loss works
[ ] Target works
[ ] Trade history works
[ ] Analytics works
[ ] Backtesting works
[ ] Walk-forward validation works
[ ] No-lookahead tests pass
[ ] WebSockets work
[ ] Reconnection works
[ ] Error handling works
[ ] Logging works
[ ] Configuration works
[ ] Docker works
[ ] README is complete
[ ] Automated tests pass
[ ] No real-money order execution exists
[ ] No fake live data is presented as real
```

---

# 82. FINAL PRODUCT PRINCIPLE

Build this as an actual quantitative research and paper-trading platform.

The objective is NOT:

> "Make a bot that always makes money."

The objective is:

> "Build a system capable of determining, through live data, historical testing, out-of-sample validation, and paper trading, whether a repeatable trading edge exists."

If the model performs poorly, the application must report that honestly.

If the model performs well, the application must still label the result as experimental and simulated.

The system should prioritize:

```text
DATA QUALITY
       ↓
NO LOOK-AHEAD BIAS
       ↓
ROBUST BACKTESTING
       ↓
RISK MANAGEMENT
       ↓
REALISTIC PAPER EXECUTION
       ↓
LIVE MONITORING
       ↓
PERFORMANCE ANALYSIS
```

Do not optimize for impressive UI at the expense of quantitative correctness.

Do not optimize for backtest profit at the expense of statistical validity.

Do not optimize for prediction accuracy at the expense of actual trading performance.

Build the entire system so that it can later be extended to additional indices, stocks, strategies, models, and—only if deliberately enabled in a future version—broker integration.

## END OF SPECIFICATION