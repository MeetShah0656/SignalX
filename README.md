# SignalX — AI NIFTY Live Paper Trading System

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![XGBoost](https://img.shields.io/badge/ML-XGBoost%20%7C%20RandomForest-orange.svg)](https://xgboost.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)](LICENSE)

SignalX is a production-quality, quantitative **AI-powered live NIFTY 50 paper-trading platform and backtesting engine** built using Python (FastAPI, SQLAlchemy, Pandas, XGBoost, Scikit-Learn) and Next.js (TypeScript, Tailwind CSS, Recharts).

---

## ⚠️ Important Safety & Execution Rules

> [!IMPORTANT]
> **PAPER TRADING ONLY:**
> This system strictly implements `PaperExecutionEngine`. It simulates order execution against live bid/ask prices and configurable slippage.
> - **NO real-money order placement endpoints exist.**
> - **NO broker order placement code is connected.**
> - **NO actual exchange orders will ever be placed.**

---

## 🚀 Key Features

1. **Live NIFTY Market Data**: Real-time quote streaming via WebSocket & REST (`yfinance` or synthetic high-frequency mock data provider).
2. **Zero-Lookahead Feature Engineering Pipeline**: Deterministic calculations of EMA 9/20/50, SMA 20/50, RSI 14, MACD, ATR 14, Bollinger Bands, Returns (1, 3, 5, 10, 20), Volume ratios, and India VIX.
3. **Machine Learning Model Engine**: XGBoost, RandomForest, and LogisticRegression models trained using chronological walk-forward splits.
4. **Dedicated Risk Engine**: Enforces data freshness thresholds, daily loss limits (2%), maximum risk per trade (1%), open position limits, and emergency kill switches.
5. **Simulated Paper Execution Engine**: Calculates ask price for BUY, bid price for SELL, and applies configurable slippage in basis points (BPS).
6. **Strategy Backtester**: Backtesting engine reusing the exact same feature pipeline and risk rules to prevent backtest-live discrepancy.
7. **Quantitative Analytics**: Win rate, profit factor, max drawdown, Sharpe ratio, Sortino ratio, and portfolio equity curve visualization.
8. **Dark Trading Terminal Interface**: Modern, responsive Next.js dark terminal UI.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12+, FastAPI, Pydantic v2, SQLAlchemy 2.0, AsyncPG / AioSQLite, Pandas, NumPy, Scikit-Learn, XGBoost, Joblib, HTTPX, WebSockets, PyTest.
- **Frontend**: Next.js 14 (App Router), TypeScript, React 18, Tailwind CSS, Recharts, Lucide React Icons.
- **Database**: PostgreSQL (production / Docker) or SQLite (instant local development).

---

## 📁 Repository Structure

```text
SignalX/
│
├── backend/
│   ├── app/
│   │   ├── api/             # REST & WebSocket Endpoints
│   │   ├── core/            # Config, Security, Logging
│   │   ├── database/        # Database Engine & SQLAlchemy Models
│   │   ├── market/          # Market Data Providers (Live & Mock)
│   │   ├── features/        # Technical Feature Engineering Pipeline
│   │   ├── ml/              # ML Model Trainer, Predictor & Registry
│   │   ├── trading/         # Risk Engine, Signals & Paper Execution
│   │   ├── backtesting/     # Backtesting Engine & Metrics
│   │   └── main.py          # FastAPI Main Entrypoint
│   ├── scripts/             # CLI Training & Backtesting Scripts
│   ├── tests/               # PyTest Test Suite
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── app/                 # Next.js App Router Pages
│   ├── components/          # Trading Terminal React Components
│   ├── package.json
│   └── tailwind.config.js
│
├── docker-compose.yml
└── README.md
```

---

## 🚦 Quick Start Guide

### 1. Prerequisites

- **Python**: `3.12+`
- **Node.js**: `18.x` or `20.x`
- **Git**

---

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (pre-configured for instant out-of-the-box operation)
cp .env.example .env

# Train initial AI ML Model (XGBoost)
python scripts/train_model.py

# Run backend development server
uvicorn app.main:app --reload --port 8000
```

Backend API documentation will be available at:
- **Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check**: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

### 3. Frontend Setup

In a new terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Install Node modules
npm install

# Start Next.js development server
npm run dev
```

Open your browser at:
- **Trading Dashboard**: [http://localhost:3000](http://localhost:3000)

---

### 4. Running with Docker Compose

You can launch the entire stack (PostgreSQL, FastAPI Backend, Next.js Frontend) using Docker:

```bash
docker compose up --build
```

---

## 🧪 Running Automated Tests

Run the backend PyTest suite to verify feature pipeline calculations, risk limits, and paper execution:

```bash
cd backend
pytest tests/ -v
```

---

## ⚖️ License & Disclaimer

This project is licensed under the MIT License.

**Disclaimer**: This application is strictly for research, educational, and paper-trading demonstration purposes. Historical backtest performance does not guarantee future results.
