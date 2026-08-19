'use client';

import React from 'react';
import { BarChart3, TrendingUp, Award, AlertTriangle, Scale } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

interface AnalyticsViewProps {
  analytics: any;
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({ analytics }) => {
  const metrics = analytics?.metrics || {};
  const equityCurve = analytics?.equity_curve || [
    { timestamp: '10:00', equity: 100000 },
    { timestamp: '11:00', equity: 100450 },
    { timestamp: '12:00', equity: 100200 },
    { timestamp: '13:00', equity: 100850 },
    { timestamp: '14:00', equity: 101200 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-blue-400" />
            <span>Quantitative Analytics & Performance</span>
          </h2>
          <p className="text-xs text-textMuted mt-1">Statistical trade analytics, risk metrics, and equity curve.</p>
        </div>
      </div>

      {/* Quantitative Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 font-mono">
        <div className="bg-card border border-border rounded-xl p-5">
          <div className="text-xs text-textMuted font-sans uppercase">Win Rate</div>
          <div className="text-3xl font-black text-emerald-400 mt-1">{metrics.win_rate || '0.0'}%</div>
          <div className="text-[11px] text-textMuted font-sans mt-1">
            {metrics.winning_trades || 0} Wins / {metrics.total_trades || 0} Trades
          </div>
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <div className="text-xs text-textMuted font-sans uppercase">Profit Factor</div>
          <div className="text-3xl font-black text-blue-400 mt-1">{metrics.profit_factor || '0.00'}</div>
          <div className="text-[11px] text-textMuted font-sans mt-1">Gross Profit / Gross Loss</div>
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <div className="text-xs text-textMuted font-sans uppercase">Max Drawdown</div>
          <div className="text-3xl font-black text-red-400 mt-1">{metrics.max_drawdown || '0.0'}%</div>
          <div className="text-[11px] text-textMuted font-sans mt-1">Peak-to-Trough Decline</div>
        </div>

        <div className="bg-card border border-border rounded-xl p-5">
          <div className="text-xs text-textMuted font-sans uppercase">Sharpe Ratio</div>
          <div className="text-3xl font-black text-purple-400 mt-1">{metrics.sharpe_ratio || '0.00'}</div>
          <div className="text-[11px] text-textMuted font-sans mt-1">Sortino: {metrics.sortino_ratio || '0.00'}</div>
        </div>
      </div>

      {/* Equity Curve Chart */}
      <div className="bg-card border border-border rounded-xl p-6 h-96 flex flex-col">
        <h3 className="font-bold text-white text-sm mb-4 flex items-center space-x-2">
          <TrendingUp className="w-4 h-4 text-emerald-400" />
          <span>Paper Portfolio Equity Curve</span>
        </h3>
        <div className="flex-1 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={equityCurve} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
              <defs>
                <linearGradient id="equityGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10B981" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#10B981" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#2A3447" vertical={false} />
              <XAxis dataKey="timestamp" stroke="#94A3B8" tick={{ fontSize: 11 }} />
              <YAxis domain={['auto', 'auto']} orientation="right" stroke="#94A3B8" tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ backgroundColor: '#151921', borderColor: '#2A3447', borderRadius: '8px', color: '#FFF' }} />
              <Area type="monotone" dataKey="equity" stroke="#10B981" strokeWidth={2} fillOpacity={1} fill="url(#equityGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
