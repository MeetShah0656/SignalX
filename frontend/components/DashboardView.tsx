'use client';

import React, { useState } from 'react';
import { CandlestickChart } from './CandlestickChart';
import { 
  Play, 
  XCircle, 
  ArrowUpRight, 
  ArrowDownRight, 
  ShieldCheck, 
  AlertTriangle, 
  Clock, 
  Layers,
  Wallet,
  Zap
} from 'lucide-react';

interface DashboardViewProps {
  niftyQuote: any;
  prediction: any;
  candles: any[];
  timeframe: string;
  setTimeframe: (tf: string) => void;
  activePositions: any[];
  portfolio: any;
  onStartTrade: () => Promise<any>;
  onClosePosition: (id: string) => Promise<any>;
}

export const DashboardView: React.FC<DashboardViewProps> = ({
  niftyQuote,
  prediction,
  candles,
  timeframe,
  setTimeframe,
  activePositions,
  portfolio,
  onStartTrade,
  onClosePosition
}) => {
  const [tradeStatus, setTradeStatus] = useState<string | null>(null);
  const [isTrading, setIsTrading] = useState<boolean>(false);
  const [rejectionReason, setRejectionReason] = useState<string | null>(null);

  const handleStartTradeClick = async () => {
    setIsTrading(true);
    setRejectionReason(null);

    const steps = [
      "GETTING LIVE PRICE...",
      "CALCULATING FEATURES...",
      "RUNNING AI INFERENCE...",
      "CHECKING RISK LIMITS...",
      "OPENING PAPER POSITION..."
    ];

    for (const step of steps) {
      setTradeStatus(step);
      await new Promise((r) => setTimeout(r, 250));
    }

    try {
      const res = await onStartTrade();
      if (res && res.success) {
        setTradeStatus("TRADE OPENED SUCCESSFULLY!");
      } else {
        setTradeStatus("TRADE REJECTED");
        setRejectionReason(res?.reason || "Risk checks failed or low confidence.");
      }
    } catch (e: any) {
      setTradeStatus("ERROR");
      setRejectionReason(e.message || "Execution error.");
    } finally {
      setTimeout(() => {
        setIsTrading(false);
        setTradeStatus(null);
      }, 3000);
    }
  };

  const signal = prediction?.signal || 'HOLD';
  const confidence = prediction?.confidence ? (prediction.confidence * 100).toFixed(1) : '50.0';
  const expectedReturn = prediction?.expected_return ? (prediction.expected_return * 100).toFixed(2) : '0.00';
  
  const ltp = niftyQuote?.close || 24685.40;
  const targetPrice = signal === 'BUY' ? (ltp * 1.01).toFixed(2) : (ltp * 0.99).toFixed(2);
  const stopLossPrice = signal === 'BUY' ? (ltp * 0.995).toFixed(2) : (ltp * 1.005).toFixed(2);

  const activePosition = activePositions && activePositions.length > 0 ? activePositions[0] : null;

  return (
    <div className="space-y-6">
      {/* Top Metric Strip */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* NIFTY Price Card */}
        <div className="bg-card border border-border rounded-xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-xs text-textMuted font-medium uppercase tracking-wider mb-2">
            <span>LIVE NIFTY 50</span>
            <span className="flex items-center space-x-1 text-emerald-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>LIVE</span>
            </span>
          </div>
          <div className="text-3xl font-extrabold text-white font-mono">
            ₹{ltp.toLocaleString('en-IN', { minimumFractionDigits: 2 })}
          </div>
          <div className="mt-2 flex items-center space-x-2 text-xs font-semibold text-emerald-400">
            <ArrowUpRight className="w-4 h-4" />
            <span>+94.20 (+0.38%)</span>
            <span className="text-textMuted font-normal">Today</span>
          </div>
        </div>

        {/* AI Signal Card */}
        <div className="bg-card border border-border rounded-xl p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-xs text-textMuted font-medium uppercase tracking-wider mb-2">
            <span>AI SIGNAL</span>
            <span className="text-xs text-blue-400 font-semibold">{prediction?.model_version || 'xgb_v1'}</span>
          </div>
          <div className="flex items-baseline space-x-3">
            <span className={`text-3xl font-black font-mono ${
              signal === 'BUY' ? 'text-emerald-400' : signal === 'SELL' ? 'text-red-400' : 'text-amber-400'
            }`}>
              {signal}
            </span>
            <span className="text-xs font-bold text-white bg-surface border border-border px-2 py-1 rounded">
              Confidence {confidence}%
            </span>
          </div>
          <div className="mt-2 text-xs text-textMuted">
            Expected Return: <span className="font-bold text-white font-mono">{expectedReturn > '0' ? `+${expectedReturn}%` : `${expectedReturn}%`}</span> (15m horizon)
          </div>
        </div>

        {/* Paper Equity Card */}
        <div className="bg-card border border-border rounded-xl p-5">
          <div className="flex items-center justify-between text-xs text-textMuted font-medium uppercase tracking-wider mb-2">
            <span>PAPER ACCOUNT EQUITY</span>
            <Wallet className="w-4 h-4 text-blue-400" />
          </div>
          <div className="text-3xl font-extrabold text-white font-mono">
            ₹{portfolio?.equity ? portfolio.equity.toLocaleString('en-IN', { minimumFractionDigits: 2 }) : '1,00,000.00'}
          </div>
          <div className="mt-2 text-xs text-textMuted flex items-center justify-between">
            <span>Realized P&L:</span>
            <span className={`font-mono font-semibold ${portfolio?.realized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {portfolio?.realized_pnl >= 0 ? '+' : ''}₹{portfolio?.realized_pnl ? portfolio.realized_pnl.toFixed(2) : '0.00'}
            </span>
          </div>
        </div>

        {/* Risk & System Health */}
        <div className="bg-card border border-border rounded-xl p-5">
          <div className="flex items-center justify-between text-xs text-textMuted font-medium uppercase tracking-wider mb-2">
            <span>RISK & LIMITS</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="space-y-1.5 text-xs">
            <div className="flex justify-between">
              <span className="text-textMuted">Max Risk / Trade:</span>
              <span className="font-semibold text-white font-mono">1.0% (₹1,000)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-textMuted">Max Daily Loss:</span>
              <span className="font-semibold text-white font-mono">2.0% (₹2,000)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-textMuted">Execution Engine:</span>
              <span className="font-bold text-blue-400 uppercase">PAPER ONLY</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: Chart & Signal Action Panel */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Candlestick Chart (2 cols) */}
        <div className="lg:col-span-2">
          <CandlestickChart 
            candles={candles} 
            timeframe={timeframe} 
            setTimeframe={setTimeframe}
            activePosition={activePosition} 
          />
        </div>

        {/* AI Signal Action Box (1 col) */}
        <div className="bg-card border border-border rounded-xl p-6 flex flex-col justify-between space-y-6">
          <div>
            <div className="flex items-center justify-between border-b border-border pb-3 mb-4">
              <div className="flex items-center space-x-2">
                <Zap className="w-5 h-5 text-amber-400" />
                <h2 className="font-bold text-white text-base">Trade Signal Console</h2>
              </div>
              <span className="text-[11px] bg-card border border-border px-2 py-0.5 rounded text-textMuted font-mono">
                {new Date().toLocaleTimeString()}
              </span>
            </div>

            {/* Signal Details */}
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-surface border border-border">
                <div className="text-xs text-textMuted mb-1 font-semibold uppercase">Prediction Target</div>
                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="bg-card p-2 rounded border border-border">
                    <div className="text-[10px] text-textMuted uppercase">Entry</div>
                    <div className="text-xs font-bold font-mono text-white">₹{ltp}</div>
                  </div>
                  <div className="bg-card p-2 rounded border border-emerald-900/50">
                    <div className="text-[10px] text-emerald-400 uppercase">Target</div>
                    <div className="text-xs font-bold font-mono text-emerald-400">₹{targetPrice}</div>
                  </div>
                  <div className="bg-card p-2 rounded border border-red-900/50">
                    <div className="text-[10px] text-red-400 uppercase">Stop Loss</div>
                    <div className="text-xs font-bold font-mono text-red-400">₹{stopLossPrice}</div>
                  </div>
                </div>
              </div>

              {/* Status / Feedback message */}
              {tradeStatus && (
                <div className={`p-3 rounded-lg border text-xs font-mono font-semibold flex items-center space-x-2 ${
                  tradeStatus.includes('OPENED')
                    ? 'bg-emerald-950/80 border-emerald-500 text-emerald-300'
                    : tradeStatus.includes('REJECTED') || tradeStatus === 'ERROR'
                    ? 'bg-red-950/80 border-red-500 text-red-300'
                    : 'bg-blue-950/80 border-blue-500 text-blue-300 animate-pulse'
                }`}>
                  <Clock className="w-4 h-4 shrink-0" />
                  <span>{tradeStatus}</span>
                </div>
              )}

              {rejectionReason && (
                <div className="p-3 bg-red-950/40 border border-red-800/40 rounded-lg text-xs text-red-300 flex items-start space-x-2">
                  <AlertTriangle className="w-4 h-4 shrink-0 text-red-400 mt-0.5" />
                  <div>
                    <span className="font-bold">Trade Rejected: </span>
                    <span>{rejectionReason}</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Action CTA Button */}
          <div>
            <button
              onClick={handleStartTradeClick}
              disabled={isTrading || !!activePosition}
              className={`w-full py-4 rounded-xl font-black text-sm tracking-wider uppercase transition-all shadow-lg flex items-center justify-center space-x-2 ${
                activePosition
                  ? 'bg-card border border-border text-textMuted cursor-not-allowed'
                  : isTrading
                  ? 'bg-blue-600 text-white cursor-wait opacity-80'
                  : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-blue-500/25 active:scale-[0.99]'
              }`}
            >
              <Play className="w-5 h-5 fill-current" />
              <span>{activePosition ? 'PAPER POSITION ALREADY ACTIVE' : isTrading ? 'PROCESSING PAPER ORDER...' : 'START PAPER TRADE'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Active Paper Position Section */}
      {activePosition && (
        <div className="bg-card border border-emerald-500/40 rounded-xl p-6 shadow-xl relative overflow-hidden">
          <div className="flex items-center justify-between pb-4 border-b border-border mb-4">
            <div className="flex items-center space-x-3">
              <span className={`px-2.5 py-1 rounded text-xs font-black uppercase ${
                activePosition.side === 'LONG' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40' : 'bg-red-500/20 text-red-400 border border-red-500/40'
              }`}>
                SIMULATED {activePosition.side} POSITION
              </span>
              <span className="text-xs text-textMuted">Symbol: <span className="font-semibold text-white">{activePosition.symbol}</span></span>
              <span className="text-xs text-textMuted">Qty: <span className="font-semibold text-white">{activePosition.quantity}</span></span>
            </div>

            <button
              onClick={() => onClosePosition(activePosition.position_id)}
              className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white font-bold text-xs rounded-lg transition-colors flex items-center space-x-1.5 shadow-md shadow-red-600/20"
            >
              <XCircle className="w-4 h-4" />
              <span>CLOSE POSITION</span>
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 font-mono">
            <div>
              <div className="text-[11px] text-textMuted uppercase font-sans">Entry Price</div>
              <div className="text-base font-bold text-white">₹{activePosition.entry_price.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-[11px] text-textMuted uppercase font-sans">Current Price</div>
              <div className="text-base font-bold text-white">₹{activePosition.current_price.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-[11px] text-textMuted uppercase font-sans">Target</div>
              <div className="text-base font-bold text-emerald-400">₹{activePosition.target.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-[11px] text-textMuted uppercase font-sans">Stop Loss</div>
              <div className="text-base font-bold text-red-400">₹{activePosition.stop_loss.toFixed(2)}</div>
            </div>
            <div>
              <div className="text-[11px] text-textMuted uppercase font-sans">Unrealized P&L</div>
              <div className={`text-lg font-black ${activePosition.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                {activePosition.unrealized_pnl >= 0 ? '+' : ''}₹{activePosition.unrealized_pnl.toFixed(2)}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
