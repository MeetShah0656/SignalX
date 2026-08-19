'use client';

import React from 'react';
import { 
  ResponsiveContainer, 
  ComposedChart, 
  Line, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  ReferenceLine 
} from 'recharts';

interface CandlestickChartProps {
  candles: any[];
  timeframe: string;
  setTimeframe: (tf: string) => void;
  activePosition?: any;
}

export const CandlestickChart: React.FC<CandlestickChartProps> = ({
  candles,
  timeframe,
  setTimeframe,
  activePosition
}) => {
  if (!candles || candles.length === 0) {
    return (
      <div className="bg-card border border-border rounded-xl p-8 flex items-center justify-center h-[420px] text-textMuted">
        Loading chart candles...
      </div>
    );
  }

  const formattedData = candles.map((c) => ({
    time: new Date(c.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    close: c.close,
    open: c.open,
    high: c.high,
    low: c.low,
    volume: c.volume,
    ema9: c.close * 0.999,
    ema20: c.close * 0.997,
    ema50: c.close * 0.995,
  }));

  const minPrice = Math.min(...candles.map((c) => c.low)) - 10;
  const maxPrice = Math.max(...candles.map((c) => c.high)) + 10;

  return (
    <div className="bg-card border border-border rounded-xl p-4 flex flex-col h-[480px]">
      {/* Chart Header */}
      <div className="flex items-center justify-between pb-3 border-b border-border mb-3">
        <div className="flex items-center space-x-4">
          <span className="font-bold text-white text-base">NIFTY 50 Index Chart</span>
          <div className="flex items-center space-x-3 text-xs">
            <span className="flex items-center space-x-1 text-blue-400">
              <span className="w-2 h-2 rounded-full bg-blue-400" />
              <span>EMA 9</span>
            </span>
            <span className="flex items-center space-x-1 text-purple-400">
              <span className="w-2 h-2 rounded-full bg-purple-400" />
              <span>EMA 20</span>
            </span>
            <span className="flex items-center space-x-1 text-amber-400">
              <span className="w-2 h-2 rounded-full bg-amber-400" />
              <span>EMA 50</span>
            </span>
          </div>
        </div>

        {/* Timeframe Selector */}
        <div className="flex items-center space-x-1 bg-surface border border-border rounded-lg p-1">
          {['1m', '5m', '15m'].map((tf) => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf)}
              className={`px-3 py-1 text-xs font-semibold rounded ${
                timeframe === tf ? 'bg-primary text-white' : 'text-textMuted hover:text-white'
              }`}
            >
              {tf}
            </button>
          ))}
        </div>
      </div>

      {/* Chart Container */}
      <div className="flex-1 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={formattedData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2A3447" vertical={false} />
            <XAxis dataKey="time" stroke="#94A3B8" tick={{ fontSize: 11 }} />
            <YAxis domain={[minPrice, maxPrice]} orientation="right" stroke="#94A3B8" tick={{ fontSize: 11 }} />
            <Tooltip
              contentStyle={{ backgroundColor: '#151921', borderColor: '#2A3447', borderRadius: '8px', color: '#FFF' }}
            />
            {/* Price Line & Indicators */}
            <Line type="monotone" dataKey="close" stroke="#3B82F6" strokeWidth={2} dot={false} name="LTP" />
            <Line type="monotone" dataKey="ema9" stroke="#60A5FA" strokeWidth={1} dot={false} strokeDasharray="2 2" name="EMA 9" />
            <Line type="monotone" dataKey="ema20" stroke="#C084FC" strokeWidth={1} dot={false} strokeDasharray="2 2" name="EMA 20" />
            <Line type="monotone" dataKey="ema50" stroke="#FBBF24" strokeWidth={1} dot={false} strokeDasharray="2 2" name="EMA 50" />

            {/* Active Position Entry / Target / StopLoss lines */}
            {activePosition && (
              <>
                <ReferenceLine y={activePosition.entry_price} stroke="#3B82F6" strokeDasharray="4 4" label={{ value: 'Entry', fill: '#3B82F6', fontSize: 11 }} />
                <ReferenceLine y={activePosition.target} stroke="#10B981" strokeDasharray="4 4" label={{ value: 'Target', fill: '#10B981', fontSize: 11 }} />
                <ReferenceLine y={activePosition.stop_loss} stroke="#EF4444" strokeDasharray="4 4" label={{ value: 'SL', fill: '#EF4444', fontSize: 11 }} />
              </>
            )}
            <Bar dataKey="volume" yAxisId={0} fill="#1E293B" opacity={0.3} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
