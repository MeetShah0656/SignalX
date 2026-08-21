'use client';

import React, { useState, useEffect } from 'react';
import { Navbar } from '../components/Navbar';
import { DashboardView } from '../components/DashboardView';
import { LiveMarketView } from '../components/LiveMarketView';
import { PaperTradingView } from '../components/PaperTradingView';
import { TradeHistoryView } from '../components/TradeHistoryView';
import { AnalyticsView } from '../components/AnalyticsView';
import { BacktestingView } from '../components/BacktestingView';
import { AIModelView } from '../components/AIModelView';
import { SettingsView } from '../components/SettingsView';

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [niftyQuote, setNiftyQuote] = useState<any>({ close: 24685.40, bid: 24684.90, ask: 24685.90 });
  const [prediction, setPrediction] = useState<any>({ signal: 'BUY', confidence: 0.734, expected_return: 0.0042, model_version: 'xgb_v1' });
  const [candles, setCandles] = useState<any[]>([]);
  const [timeframe, setTimeframe] = useState('5m');
  const [activePositions, setActivePositions] = useState<any[]>([]);
  const [trades, setTrades] = useState<any[]>([]);
  const [portfolio, setPortfolio] = useState<any>({ initial_balance: 100000, cash_balance: 100000, equity: 100000, realized_pnl: 0, unrealized_pnl: 0 });
  const [systemStatus, setSystemStatus] = useState<any>({ market_api: 'CONNECTED', ml_model: 'READY' });
  const [analytics, setAnalytics] = useState<any>({});
  const [modelStatus, setModelStatus] = useState<any>({});

  // Initial REST API Data Fetching
  const fetchAllData = async () => {
    try {
      const [quoteRes, predRes, candlesRes, posRes, tradesRes, portRes, sysRes, analyticsRes, modelRes] = await Promise.all([
        fetch('/api/market/nifty').then((r) => r.json()).catch(() => null),
        fetch('/api/prediction/latest').then((r) => r.json()).catch(() => null),
        fetch(`/api/market/candles?timeframe=${timeframe}`).then((r) => r.json()).catch(() => []),
        fetch('/api/trading/positions').then((r) => r.json()).catch(() => []),
        fetch('/api/trading/trades').then((r) => r.json()).catch(() => []),
        fetch('/api/portfolio').then((r) => r.json()).catch(() => null),
        fetch('/api/system/status').then((r) => r.json()).catch(() => null),
        fetch('/api/analytics').then((r) => r.json()).catch(() => ({})),
        fetch('/api/model/status').then((r) => r.json()).catch(() => ({})),
      ]);

      if (quoteRes) setNiftyQuote(quoteRes);
      if (predRes) setPrediction(predRes);
      if (Array.isArray(candlesRes) && candlesRes.length > 0) setCandles(candlesRes);
      if (Array.isArray(posRes)) setActivePositions(posRes);
      if (Array.isArray(tradesRes)) setTrades(tradesRes);
      if (portRes) setPortfolio(portRes);
      if (sysRes) setSystemStatus(sysRes);
      if (analyticsRes) setAnalytics(analyticsRes);
      if (modelRes) setModelStatus(modelRes);
    } catch (e) {
      console.error('Error fetching dashboard data:', e);
    }
  };

  useEffect(() => {
    fetchAllData();
    const interval = setInterval(fetchAllData, 5000);
    return () => clearInterval(interval);
  }, [timeframe]);

  // WebSocket connection for live quote stream
  useEffect(() => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.hostname}:8000/ws/market`;
    let ws: WebSocket | null = null;

    try {
      ws = new WebSocket(wsUrl);
      ws.onmessage = (event) => {
        try {
          const parsed = JSON.parse(event.data);
          if (parsed.event === 'market_update' && parsed.data) {
            setNiftyQuote(parsed.data);
          } else if (parsed.event === 'portfolio_update' && parsed.data) {
            setPortfolio((prev) => ({ ...prev, ...parsed.data }));
            if (parsed.data.open_positions) setActivePositions(parsed.data.open_positions);
          }
        } catch (err) {
          // parse error
        }
      };
    } catch (e) {
      console.warn('WebSocket connection error:', e);
    }

    return () => {
      if (ws) ws.close();
    };
  }, []);

  const handleStartTrade = async () => {
    const res = await fetch('/api/trading/start', { method: 'POST' }).then((r) => r.json());
    await fetchAllData();
    return res;
  };

  const handleClosePosition = async (id: string) => {
    const res = await fetch(`/api/trading/close?position_id=${id}`, { method: 'POST' }).then((r) => r.json());
    await fetchAllData();
    return res;
  };

  const handlePauseTrading = async () => {
    const res = await fetch('/api/trading/pause', { method: 'POST' }).then((r) => r.json());
    await fetchAllData();
    return res;
  };

  const handleResumeTrading = async () => {
    const res = await fetch('/api/trading/resume', { method: 'POST' }).then((r) => r.json());
    await fetchAllData();
    return res;
  };

  const handleResetAccount = async () => {
    const res = await fetch('/api/portfolio/reset', { method: 'POST' }).then((r) => r.json());
    await fetchAllData();
    return res;
  };

  const handleRunBacktest = async (params: any) => {
    const res = await fetch('/api/backtest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    }).then((r) => r.json());
    return res;
  };

  const handleTrainModel = async (params: any) => {
    const res = await fetch('/api/model/train', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    }).then((r) => r.json());
    await fetchAllData();
    return res;
  };

  return (
    <div className="min-h-screen bg-background text-white flex flex-col font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemStatus={systemStatus}
        portfolio={portfolio}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 md:p-6">
        {activeTab === 'dashboard' && (
          <DashboardView
            niftyQuote={niftyQuote}
            prediction={prediction}
            candles={candles}
            timeframe={timeframe}
            setTimeframe={setTimeframe}
            activePositions={activePositions}
            portfolio={portfolio}
            systemStatus={systemStatus}
            onStartTrade={handleStartTrade}
            onClosePosition={handleClosePosition}
          />
        )}
        {activeTab === 'live_market' && <LiveMarketView niftyQuote={niftyQuote} candles={candles} />}
        {activeTab === 'paper_trading' && (
          <PaperTradingView
            portfolio={portfolio}
            activePositions={activePositions}
            onClosePosition={handleClosePosition}
            onPauseTrading={handlePauseTrading}
            onResumeTrading={handleResumeTrading}
            onResetAccount={handleResetAccount}
          />
        )}
        {activeTab === 'history' && <TradeHistoryView trades={trades} />}
        {activeTab === 'analytics' && <AnalyticsView analytics={analytics} />}
        {activeTab === 'backtesting' && <BacktestingView onRunBacktest={handleRunBacktest} />}
        {activeTab === 'ai_model' && <AIModelView modelStatus={modelStatus} onTrainModel={handleTrainModel} />}
        {activeTab === 'settings' && <SettingsView />}
      </main>

      <footer className="bg-surface border-t border-border py-4 text-center text-xs text-textMuted font-mono">
        SignalX AI Paper Trading Engine • Built with FastAPI, Next.js, PyTorch/XGBoost • Simulated Trading Environment
      </footer>
    </div>
  );
}
