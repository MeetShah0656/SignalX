'use client';

import React, { useState } from 'react';
import { 
  ResponsiveContainer, 
  ComposedChart, 
  Line, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  CartesianGrid, 
  ReferenceLine,
  Brush
} from 'recharts';
import { ZoomIn, ZoomOut, RotateCcw, Calendar, Eye, EyeOff } from 'lucide-react';

interface CandlestickChartProps {
  candles: any[];
  timeframe: string;
  setTimeframe: (tf: string) => void;
  activePosition?: any;
}

// Pure TradingView / Zerodha Style Candlestick SVG Shape (OHLC Box + Wicks)
const CustomCandleBar = (props: any) => {
  const { x, width, payload, yAxis } = props;
  if (!payload || !yAxis) return null;

  const { open, high, low, close } = payload;
  const isUp = close >= open;
  
  // Vibrant Trading Colors (Bullish Green & Bearish Red)
  const strokeColor = isUp ? '#10B981' : '#EF4444';
  const fillColor = isUp ? '#10B981' : '#EF4444';

  const openY = yAxis.scale(open);
  const closeY = yAxis.scale(close);
  const highY = yAxis.scale(high);
  const lowY = yAxis.scale(low);

  const candleWidth = Math.max(4, width * 0.75);
  const candleX = x + (width - candleWidth) / 2;
  const boxY = Math.min(openY, closeY);
  const boxHeight = Math.max(3, Math.abs(openY - closeY));
  const centerX = x + width / 2;

  return (
    <g className="candlestick-bar group cursor-pointer">
      {/* High-Low Wick Line */}
      <line
        x1={centerX}
        y1={highY}
        x2={centerX}
        y2={lowY}
        stroke={strokeColor}
        strokeWidth={1.5}
        strokeLinecap="round"
      />
      {/* Open-Close Body Box */}
      <rect
        x={candleX}
        y={boxY}
        width={candleWidth}
        height={boxHeight}
        fill={fillColor}
        stroke={strokeColor}
        strokeWidth={1}
        rx={1}
        className="transition-all duration-150 group-hover:brightness-125"
      />
    </g>
  );
};

export const CandlestickChart: React.FC<CandlestickChartProps> = ({
  candles,
  timeframe,
  setTimeframe,
  activePosition
}) => {
  const [zoomRange, setZoomRange] = useState<{ startIndex: number; endIndex: number } | null>(null);
  const [showIndicators, setShowIndicators] = useState<boolean>(true);

  if (!candles || candles.length === 0) {
    return (
      <div className="bg-card border border-border rounded-xl p-8 flex items-center justify-center h-[520px] text-textMuted">
        Loading live NIFTY 50 candlestick chart...
      </div>
    );
  }

  // Calculate EMA 9, 20, 50
  const closes = candles.map(c => c.close);
  const calcEMA = (period: number) => {
    const k = 2 / (period + 1);
    let ema = closes[0];
    return closes.map(price => {
      ema = price * k + ema * (1 - k);
      return Math.round(ema * 100) / 100;
    });
  };

  const ema9Arr = calcEMA(9);
  const ema20Arr = calcEMA(20);
  const ema50Arr = calcEMA(50);

  const formattedData = candles.map((c, i) => {
    const ts = new Date(c.timestamp);
    const isValidDate = !isNaN(ts.getTime());
    
    const dateLabel = isValidDate 
      ? ts.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
      : '';
    const timeLabel = isValidDate
      ? ts.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      : String(c.timestamp);

    const fullTimeStr = dateLabel ? `${dateLabel}, ${timeLabel}` : timeLabel;

    return {
      time: fullTimeStr,
      dateStr: isValidDate ? ts.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '',
      rawTime: timeLabel,
      open: c.open,
      high: c.high,
      low: c.low,
      close: c.close,
      volume: c.volume,
      ema9: ema9Arr[i],
      ema20: ema20Arr[i],
      ema50: ema50Arr[i]
    };
  });

  const activeData = zoomRange 
    ? formattedData.slice(zoomRange.startIndex, zoomRange.endIndex + 1)
    : formattedData;

  const validLows = activeData.map((c) => c.low).filter(v => typeof v === 'number' && !isNaN(v));
  const validHighs = activeData.map((c) => c.high).filter(v => typeof v === 'number' && !isNaN(v));

  const minPrice = validLows.length > 0 ? Math.floor(Math.min(...validLows) - 8) : 24000;
  const maxPrice = validHighs.length > 0 ? Math.ceil(Math.max(...validHighs) + 8) : 24200;
  const maxVolume = Math.max(...activeData.map(c => c.volume || 0), 100);

  // Zoom Action Handlers
  const handleZoomIn = () => {
    const total = formattedData.length;
    const currentStart = zoomRange ? zoomRange.startIndex : 0;
    const currentEnd = zoomRange ? zoomRange.endIndex : total - 1;
    const count = currentEnd - currentStart;
    if (count > 15) {
      const newStart = Math.min(currentStart + Math.floor(count * 0.2), total - 15);
      setZoomRange({ startIndex: newStart, endIndex: currentEnd });
    }
  };

  const handleZoomOut = () => {
    if (!zoomRange) return;
    const total = formattedData.length;
    const newStart = Math.max(0, zoomRange.startIndex - Math.floor((zoomRange.endIndex - zoomRange.startIndex) * 0.3));
    const newEnd = Math.min(total - 1, zoomRange.endIndex + Math.floor((zoomRange.endIndex - zoomRange.startIndex) * 0.3));
    if (newStart === 0 && newEnd === total - 1) {
      setZoomRange(null);
    } else {
      setZoomRange({ startIndex: newStart, endIndex: newEnd });
    }
  };

  const handleResetZoom = () => {
    setZoomRange(null);
  };

  const startDateStr = formattedData[0]?.dateStr || '';
  const endDateStr = formattedData[formattedData.length - 1]?.dateStr || '';

  return (
    <div className="bg-card border border-border rounded-xl p-4 flex flex-col h-[520px]">
      {/* Chart Header */}
      <div className="flex items-center justify-between pb-3 border-b border-border mb-3">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
            <span className="font-bold text-white text-base">NSE NIFTY 50 Candlestick Terminal</span>
          </div>

          {/* Date Badge */}
          <div className="hidden md:flex items-center space-x-1.5 text-xs text-textMuted bg-surface border border-border px-2.5 py-1 rounded-md font-mono">
            <Calendar className="w-3.5 h-3.5 text-blue-400" />
            <span>{startDateStr} - {endDateStr}</span>
          </div>
        </div>

        {/* Chart Controls Toolbar */}
        <div className="flex items-center space-x-3">
          {/* Indicator Toggle */}
          <button
            onClick={() => setShowIndicators(!showIndicators)}
            className={`flex items-center space-x-1 px-2.5 py-1 text-xs font-semibold rounded border transition-colors ${
              showIndicators 
                ? 'bg-blue-500/10 border-blue-500/30 text-blue-400' 
                : 'bg-surface border-border text-textMuted hover:text-white'
            }`}
            title="Toggle Technical EMA Overlay Lines"
          >
            {showIndicators ? <Eye className="w-3.5 h-3.5" /> : <EyeOff className="w-3.5 h-3.5" />}
            <span>EMA Overlay</span>
          </button>

          {/* Zoom & Reset Controls */}
          <div className="flex items-center space-x-1 bg-surface border border-border rounded-lg p-1">
            <button
              onClick={handleZoomIn}
              title="Zoom In"
              className="p-1.5 text-textMuted hover:text-white hover:bg-card rounded transition-colors"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={handleZoomOut}
              title="Zoom Out"
              className="p-1.5 text-textMuted hover:text-white hover:bg-card rounded transition-colors"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <button
              onClick={handleResetZoom}
              title="Reset Zoom & Scroll"
              className="p-1.5 text-textMuted hover:text-white hover:bg-card rounded transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
          </div>

          {/* Timeframe Selector */}
          <div className="flex items-center space-x-1 bg-surface border border-border rounded-lg p-1">
            {['1m', '5m', '15m'].map((tf) => (
              <button
                key={tf}
                onClick={() => {
                  setTimeframe(tf);
                  setZoomRange(null);
                }}
                className={`px-3 py-1 text-xs font-semibold rounded transition-all ${
                  timeframe === tf ? 'bg-primary text-white shadow' : 'text-textMuted hover:text-white'
                }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Chart Container */}
      <div className="flex-1 w-full relative">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={formattedData} margin={{ top: 10, right: 10, left: 10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2A3447" vertical={false} />
            
            {/* XAxis displaying Date + Time */}
            <XAxis 
              dataKey="time" 
              stroke="#94A3B8" 
              tick={{ fontSize: 10 }}
              interval="preserveStartEnd"
              minTickGap={30}
            />
            
            {/* Price YAxis */}
            <YAxis 
              yAxisId="price" 
              domain={[minPrice, maxPrice]} 
              orientation="right" 
              stroke="#94A3B8" 
              tick={{ fontSize: 11 }} 
              tickFormatter={(v) => v.toFixed(0)}
            />

            {/* Volume YAxis */}
            <YAxis 
              yAxisId="volume" 
              domain={[0, maxVolume * 4]} 
              hide={true} 
            />

            {/* Tooltip displaying full Date, Time, OHLC, Volume */}
            <Tooltip
              content={({ active, payload }) => {
                if (active && payload && payload.length) {
                  const data = payload[0].payload;
                  const isUp = data.close >= data.open;
                  return (
                    <div className="bg-surface border border-border rounded-lg p-3 text-xs space-y-1 font-mono shadow-2xl text-white">
                      <div className="text-textMuted font-sans font-bold border-b border-border pb-1 mb-1 flex justify-between">
                        <span>Date & Time:</span>
                        <span className="text-blue-400">{data.time}</span>
                      </div>
                      <div className="flex justify-between space-x-4">
                        <span className="text-textMuted">Open:</span>
                        <span className="font-bold">₹{data.open?.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between space-x-4">
                        <span className="text-textMuted">High:</span>
                        <span className="font-bold text-emerald-400">₹{data.high?.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between space-x-4">
                        <span className="text-textMuted">Low:</span>
                        <span className="font-bold text-red-400">₹{data.low?.toFixed(2)}</span>
                      </div>
                      <div className="flex justify-between space-x-4">
                        <span className="text-textMuted">Close (LTP):</span>
                        <span className={`font-bold ${isUp ? 'text-emerald-400' : 'text-red-400'}`}>
                          ₹{data.close?.toFixed(2)}
                        </span>
                      </div>
                      <div className="flex justify-between space-x-4 pt-1 border-t border-border">
                        <span className="text-textMuted">Volume:</span>
                        <span className="font-bold text-blue-400">{data.volume?.toLocaleString()}</span>
                      </div>
                    </div>
                  );
                }
                return null;
              }}
            />

            {/* Volume Bars */}
            <Bar dataKey="volume" yAxisId="volume" fill="#1E293B" opacity={0.3} />

            {/* Pure Financial Candlestick Bars */}
            <Bar dataKey="close" yAxisId="price" shape={<CustomCandleBar />} />

            {/* Technical EMA Line Overlays (Optional) */}
            {showIndicators && (
              <>
                <Line yAxisId="price" type="monotone" dataKey="ema9" stroke="#60A5FA" strokeWidth={1.5} dot={false} name="EMA 9" />
                <Line yAxisId="price" type="monotone" dataKey="ema20" stroke="#C084FC" strokeWidth={1.5} dot={false} name="EMA 20" />
                <Line yAxisId="price" type="monotone" dataKey="ema50" stroke="#FBBF24" strokeWidth={1.5} dot={false} name="EMA 50" />
              </>
            )}

            {/* Active Position Overlay Lines */}
            {activePosition && (
              <>
                <ReferenceLine yAxisId="price" y={activePosition.entry_price} stroke="#3B82F6" strokeDasharray="4 4" label={{ value: 'Entry', fill: '#3B82F6', fontSize: 11 }} />
                <ReferenceLine yAxisId="price" y={activePosition.target} stroke="#10B981" strokeDasharray="4 4" label={{ value: 'Target', fill: '#10B981', fontSize: 11 }} />
                <ReferenceLine yAxisId="price" y={activePosition.stop_loss} stroke="#EF4444" strokeDasharray="4 4" label={{ value: 'SL', fill: '#EF4444', fontSize: 11 }} />
              </>
            )}

            {/* Interactive Brush Scroll & Zoom Slider */}
            <Brush 
              dataKey="time" 
              height={24} 
              stroke="#3B82F6" 
              fill="#151921"
              tickFormatter={() => ''}
              startIndex={zoomRange ? zoomRange.startIndex : Math.max(0, formattedData.length - 80)}
              endIndex={zoomRange ? zoomRange.endIndex : formattedData.length - 1}
              onChange={(range) => {
                if (range && typeof range.startIndex === 'number' && typeof range.endIndex === 'number') {
                  setZoomRange({ startIndex: range.startIndex, endIndex: range.endIndex });
                }
              }}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
