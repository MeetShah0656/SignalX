'use client';

import React, { useState } from 'react';
import { SlidersHorizontal, Play, CheckCircle2, TrendingUp, BarChart2 } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

interface BacktestingViewProps {
  onRunBacktest: (params: any) => Promise<any>;
}

export const BacktestingView: React.FC<BacktestingViewProps> = ({ onRunBacktest }) => {
  const [initialCapital, setInitialCapital] = useState(100000);
  const [timeframe, setTimeframe] = useState('5m');
  const [buyThreshold, setBuyThreshold] = useState(0.65);
  const [sellThreshold, setSellThreshold] = useState(0.65);
  const [stopLossPct, setStopLossPct] = useState(0.005);
  const [targetPct, setTargetPct] = useState(0.010);

  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<any>(null);

  const handleRunBacktest = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsRunning(true);
    try {
      const res = await onRunBacktest({
        initial_capital: initialCapital,
        timeframe,
        buy_threshold: buyThreshold,
        sell_threshold: sellThreshold,
        stop_loss_pct: stopLossPct,
        target_pct: targetPct
      });
      setResults(res);
    } catch (err) {
      console.error(err);
    } finally {
      setIsRunning(false);
    }
  };

  const metrics = results?.metrics || {};

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <SlidersHorizontal className="w-5 h-5 text-blue-400" />
            <span>Strategy Backtester Engine</span>
          </h2>
          <p className="text-xs text-textMuted mt-1">Test ML strategy parameters against historical NIFTY 50 candles with identical execution rules.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Backtest Config Form */}
        <div className="bg-card border border-border rounded-xl p-6">
          <h3 className="font-bold text-white text-sm mb-4">Backtest Configuration</h3>

          <form onSubmit={handleRunBacktest} className="space-y-4 text-xs font-mono">
            <div>
              <label className="text-textMuted font-sans block mb-1">Initial Capital (₹)</label>
              <input
                type="number"
                value={initialCapital}
                onChange={(e) => setInitialCapital(Number(e.target.value))}
                className="w-full bg-surface border border-border rounded-lg p-2 text-white focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="text-textMuted font-sans block mb-1">Timeframe</label>
              <select
                value={timeframe}
                onChange={(e) => setTimeframe(e.target.value)}
                className="w-full bg-surface border border-border rounded-lg p-2 text-white focus:outline-none focus:border-primary"
              >
                <option value="1m">1 Minute Candles</option>
                <option value="5m">5 Minute Candles (Default)</option>
                <option value="15m">15 Minute Candles</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-textMuted font-sans block mb-1">BUY Threshold</label>
                <input
                  type="number"
                  step="0.05"
                  value={buyThreshold}
                  onChange={(e) => setBuyThreshold(Number(e.target.value))}
                  className="w-full bg-surface border border-border rounded-lg p-2 text-white focus:outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="text-textMuted font-sans block mb-1">SELL Threshold</label>
                <input
                  type="number"
                  step="0.05"
                  value={sellThreshold}
                  onChange={(e) => setSellThreshold(Number(e.target.value))}
                  className="w-full bg-surface border border-border rounded-lg p-2 text-white focus:outline-none focus:border-primary"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-textMuted font-sans block mb-1">Stop Loss (%)</label>
                <input
                  type="number"
                  step="0.001"
                  value={stopLossPct}
                  onChange={(e) => setStopLossPct(Number(e.target.value))}
                  className="w-full bg-surface border border-border rounded-lg p-2 text-white focus:outline-none focus:border-primary"
                />
              </div>
              <div>
                <label className="text-textMuted font-sans block mb-1">Target Profit (%)</label>
                <input
                  type="number"
                  step="0.001"
                  value={targetPct}
                  onChange={(e) => setTargetPct(Number(e.target.value))}
                  className="w-full bg-surface border border-border rounded-lg p-2 text-white focus:outline-none focus:border-primary"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isRunning}
              className="w-full py-3 bg-primary hover:bg-blue-600 text-white font-bold rounded-xl transition-all shadow-lg shadow-primary/20 flex items-center justify-center space-x-2 mt-4"
            >
              <Play className="w-4 h-4 fill-current" />
              <span>{isRunning ? 'RUNNING SIMULATION...' : 'EXECUTE BACKTEST'}</span>
            </button>
          </form>
        </div>

        {/* Results Panel */}
        <div className="lg:col-span-2 space-y-6">
          {results ? (
            <>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono">
                <div className="bg-card border border-border rounded-xl p-4">
                  <div className="text-[11px] text-textMuted uppercase font-sans">Total Return</div>
                  <div className={`text-2xl font-black mt-1 ${metrics.total_return >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {metrics.total_return >= 0 ? '+' : ''}{metrics.total_return}%
                  </div>
                </div>
                <div className="bg-card border border-border rounded-xl p-4">
                  <div className="text-[11px] text-textMuted uppercase font-sans">Win Rate</div>
                  <div className="text-2xl font-black text-white mt-1">{metrics.win_rate}%</div>
                </div>
                <div className="bg-card border border-border rounded-xl p-4">
                  <div className="text-[11px] text-textMuted uppercase font-sans">Profit Factor</div>
                  <div className="text-2xl font-black text-blue-400 mt-1">{metrics.profit_factor}</div>
                </div>
                <div className="bg-card border border-border rounded-xl p-4">
                  <div className="text-[11px] text-textMuted uppercase font-sans">Max Drawdown</div>
                  <div className="text-2xl font-black text-red-400 mt-1">{metrics.max_drawdown}%</div>
                </div>
              </div>

              {/* Backtest Equity Curve */}
              <div className="bg-card border border-border rounded-xl p-6 h-80 flex flex-col">
                <h4 className="font-bold text-white text-xs uppercase mb-3 flex items-center space-x-2">
                  <TrendingUp className="w-4 h-4 text-emerald-400" />
                  <span>Simulated Equity Growth Curve</span>
                </h4>
                <div className="flex-1 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={results.equity_curve} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#2A3447" vertical={false} />
                      <XAxis dataKey="timestamp" stroke="#94A3B8" tick={{ fontSize: 10 }} />
                      <YAxis domain={['auto', 'auto']} orientation="right" stroke="#94A3B8" tick={{ fontSize: 10 }} />
                      <Tooltip contentStyle={{ backgroundColor: '#151921', borderColor: '#2A3447', borderRadius: '8px', color: '#FFF' }} />
                      <Area type="monotone" dataKey="equity" stroke="#3B82F6" strokeWidth={2} fillOpacity={0.3} fill="#3B82F6" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </>
          ) : (
            <div className="bg-card border border-border rounded-xl p-12 flex flex-col items-center justify-center text-center text-textMuted h-full space-y-3">
              <BarChart2 className="w-12 h-12 text-border" />
              <div>
                <h4 className="font-bold text-white text-sm">No Backtest Executed Yet</h4>
                <p className="text-xs text-textMuted mt-1">Configure strategy parameters on the left and click Execute Backtest to simulate.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
