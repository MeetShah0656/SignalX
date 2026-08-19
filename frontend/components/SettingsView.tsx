'use client';

import React, { useState } from 'react';
import { Settings, Save, CheckCircle } from 'lucide-react';

export const SettingsView: React.FC = () => {
  const [provider, setProvider] = useState('mock');
  const [buyThreshold, setBuyThreshold] = useState(0.65);
  const [sellThreshold, setSellThreshold] = useState(0.65);
  const [maxRisk, setMaxRisk] = useState(0.01);
  const [maxDailyLoss, setMaxDailyLoss] = useState(0.02);
  const [slippageBps, setSlippageBps] = useState(5.0);
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-4xl">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <Settings className="w-5 h-5 text-blue-400" />
            <span>Application & Strategy Settings</span>
          </h2>
          <p className="text-xs text-textMuted mt-1">Configure trading thresholds, risk limits, slippage parameters, and data providers.</p>
        </div>
      </div>

      <form onSubmit={handleSave} className="space-y-6">
        {/* Market Data Provider Card */}
        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-bold text-white text-sm">Market Data Provider Configuration</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            <div>
              <label className="text-textMuted font-sans block mb-1">Active Market Data Provider</label>
              <select
                value={provider}
                onChange={(e) => setProvider(e.target.value)}
                className="w-full bg-surface border border-border rounded-lg p-2 text-white focus:outline-none focus:border-primary"
              >
                <option value="mock">Mock / Simulated Data Provider (Default)</option>
                <option value="yfinance">Yahoo Finance Live Ticker (^NSEI)</option>
                <option value="broker">Custom Broker REST / WebSocket API</option>
              </select>
            </div>

            <div>
              <label className="text-textMuted font-sans block mb-1">Market Symbol</label>
              <input
                type="text"
                value="NIFTY 50 (^NSEI)"
                disabled
                className="w-full bg-surface border border-border rounded-lg p-2 text-textMuted cursor-not-allowed"
              />
            </div>
          </div>
        </div>

        {/* Strategy Signal Thresholds */}
        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-bold text-white text-sm">Signal Probability Thresholds</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
            <div>
              <label className="text-textMuted font-sans block mb-1">BUY Probability Threshold (0.50 - 0.95)</label>
              <input
                type="number"
                step="0.05"
                value={buyThreshold}
                onChange={(e) => setBuyThreshold(Number(e.target.value))}
                className="w-full bg-surface border border-border rounded-lg p-2 text-white focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="text-textMuted font-sans block mb-1">SELL Probability Threshold (0.50 - 0.95)</label>
              <input
                type="number"
                step="0.05"
                value={sellThreshold}
                onChange={(e) => setSellThreshold(Number(e.target.value))}
                className="w-full bg-surface border border-border rounded-lg p-2 text-white focus:outline-none focus:border-primary"
              />
            </div>
          </div>
        </div>

        {/* Risk & Execution Settings */}
        <div className="bg-card border border-border rounded-xl p-6 space-y-4">
          <h3 className="font-bold text-white text-sm">Risk Management & Simulated Execution</h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs font-mono">
            <div>
              <label className="text-textMuted font-sans block mb-1">Max Risk per Trade (%)</label>
              <input
                type="number"
                step="0.005"
                value={maxRisk}
                onChange={(e) => setMaxRisk(Number(e.target.value))}
                className="w-full bg-surface border border-border rounded-lg p-2 text-white focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="text-textMuted font-sans block mb-1">Max Daily Loss (%)</label>
              <input
                type="number"
                step="0.005"
                value={maxDailyLoss}
                onChange={(e) => setMaxDailyLoss(Number(e.target.value))}
                className="w-full bg-surface border border-border rounded-lg p-2 text-white focus:outline-none focus:border-primary"
              />
            </div>

            <div>
              <label className="text-textMuted font-sans block mb-1">Simulated Slippage (BPS)</label>
              <input
                type="number"
                step="1"
                value={slippageBps}
                onChange={(e) => setSlippageBps(Number(e.target.value))}
                className="w-full bg-surface border border-border rounded-lg p-2 text-white focus:outline-none focus:border-primary"
              />
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between">
          {saved && (
            <div className="flex items-center space-x-2 text-xs font-semibold text-emerald-400">
              <CheckCircle className="w-4 h-4" />
              <span>Settings updated successfully!</span>
            </div>
          )}
          <button
            type="submit"
            className="ml-auto px-6 py-3 bg-primary hover:bg-blue-600 text-white font-bold text-xs rounded-xl shadow-lg shadow-primary/20 flex items-center space-x-2 transition-all"
          >
            <Save className="w-4 h-4" />
            <span>SAVE CONFIGURATION</span>
          </button>
        </div>
      </form>
    </div>
  );
};
