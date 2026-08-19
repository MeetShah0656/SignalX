'use client';

import React, { useState } from 'react';
import { PlaySquare, ShieldAlert, RefreshCw, XCircle, Pause, Play, AlertOctagon } from 'lucide-react';

interface PaperTradingViewProps {
  portfolio: any;
  activePositions: any[];
  onClosePosition: (id: string) => Promise<any>;
  onPauseTrading: () => Promise<any>;
  onResumeTrading: () => Promise<any>;
  onResetAccount: () => Promise<any>;
}

export const PaperTradingView: React.FC<PaperTradingViewProps> = ({
  portfolio,
  activePositions,
  onClosePosition,
  onPauseTrading,
  onResumeTrading,
  onResetAccount
}) => {
  const [showResetModal, setShowResetModal] = useState(false);

  const isPaused = portfolio?.is_trading_paused;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <PlaySquare className="w-5 h-5 text-blue-400" />
            <span>Virtual Paper Trading Control Center</span>
          </h2>
          <p className="text-xs text-textMuted mt-1">Manage virtual positions, emergency kill switch, and account balance.</p>
        </div>

        <div className="flex items-center space-x-3">
          {/* Pause / Resume Kill Switch */}
          <button
            onClick={isPaused ? onResumeTrading : onPauseTrading}
            className={`px-4 py-2 rounded-lg font-bold text-xs flex items-center space-x-2 transition-all shadow-md ${
              isPaused
                ? 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-emerald-600/20'
                : 'bg-amber-600 hover:bg-amber-500 text-white shadow-amber-600/20'
            }`}
          >
            {isPaused ? <Play className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
            <span>{isPaused ? 'RESUME TRADING' : 'PAUSE TRADING (KILL SWITCH)'}</span>
          </button>

          {/* Reset Paper Account Button */}
          <button
            onClick={() => setShowResetModal(true)}
            className="px-4 py-2 bg-card border border-border hover:border-red-500 text-textMuted hover:text-red-400 font-bold text-xs rounded-lg transition-all flex items-center space-x-1.5"
          >
            <RefreshCw className="w-4 h-4" />
            <span>RESET ACCOUNT</span>
          </button>
        </div>
      </div>

      {/* Account Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 font-mono">
        <div className="bg-card border border-border rounded-xl p-5">
          <div className="text-xs text-textMuted uppercase font-sans">Initial Capital</div>
          <div className="text-2xl font-bold text-white mt-1">
            ₹{portfolio?.initial_balance ? portfolio.initial_balance.toLocaleString('en-IN') : '1,00,000'}
          </div>
        </div>
        <div className="bg-card border border-border rounded-xl p-5">
          <div className="text-xs text-textMuted uppercase font-sans">Cash Balance</div>
          <div className="text-2xl font-bold text-white mt-1">
            ₹{portfolio?.cash_balance ? portfolio.cash_balance.toLocaleString('en-IN', { minimumFractionDigits: 2 }) : '1,00,000.00'}
          </div>
        </div>
        <div className="bg-card border border-border rounded-xl p-5">
          <div className="text-xs text-textMuted uppercase font-sans">Current Equity</div>
          <div className="text-2xl font-black text-blue-400 mt-1">
            ₹{portfolio?.equity ? portfolio.equity.toLocaleString('en-IN', { minimumFractionDigits: 2 }) : '1,00,000.00'}
          </div>
        </div>
        <div className="bg-card border border-border rounded-xl p-5">
          <div className="text-xs text-textMuted uppercase font-sans">Total Realized P&L</div>
          <div className={`text-2xl font-black mt-1 ${portfolio?.realized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {portfolio?.realized_pnl >= 0 ? '+' : ''}₹{portfolio?.realized_pnl ? portfolio.realized_pnl.toFixed(2) : '0.00'}
          </div>
        </div>
      </div>

      {/* Active Positions Table */}
      <div className="bg-card border border-border rounded-xl p-6">
        <h3 className="font-bold text-white text-sm mb-4">Active Virtual Positions ({activePositions.length})</h3>

        {activePositions.length === 0 ? (
          <div className="p-8 text-center text-textMuted text-xs bg-surface border border-border rounded-xl">
            No active virtual positions currently open. Click <span className="font-bold text-blue-400">START PAPER TRADE</span> on the dashboard to evaluate AI signals and open a paper trade.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-surface text-textMuted font-sans uppercase border-b border-border">
                <tr>
                  <th className="p-3">Symbol</th>
                  <th className="p-3">Side</th>
                  <th className="p-3">Qty</th>
                  <th className="p-3">Entry Price</th>
                  <th className="p-3">Current Price</th>
                  <th className="p-3">Target</th>
                  <th className="p-3">Stop Loss</th>
                  <th className="p-3">Unrealized P&L</th>
                  <th className="p-3">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {activePositions.map((pos) => (
                  <tr key={pos.position_id} className="hover:bg-surface/50">
                    <td className="p-3 font-bold text-white">{pos.symbol}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded font-bold ${pos.side === 'LONG' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                        {pos.side}
                      </span>
                    </td>
                    <td className="p-3 text-white">{pos.quantity}</td>
                    <td className="p-3 text-white">₹{pos.entry_price.toFixed(2)}</td>
                    <td className="p-3 text-white">₹{pos.current_price.toFixed(2)}</td>
                    <td className="p-3 text-emerald-400">₹{pos.target.toFixed(2)}</td>
                    <td className="p-3 text-red-400">₹{pos.stop_loss.toFixed(2)}</td>
                    <td className={`p-3 font-bold ${pos.unrealized_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {pos.unrealized_pnl >= 0 ? '+' : ''}₹{pos.unrealized_pnl.toFixed(2)}
                    </td>
                    <td className="p-3">
                      <button
                        onClick={() => onClosePosition(pos.position_id)}
                        className="px-3 py-1 bg-red-600 hover:bg-red-500 text-white font-bold rounded text-[11px]"
                      >
                        CLOSE
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Reset Confirmation Modal */}
      {showResetModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-card border border-border rounded-xl max-w-md w-full p-6 space-y-4">
            <div className="flex items-center space-x-3 text-red-400">
              <AlertOctagon className="w-6 h-6" />
              <h3 className="text-lg font-bold text-white">Reset Paper Trading Account</h3>
            </div>
            <p className="text-xs text-textMuted leading-relaxed">
              Are you sure you want to reset your paper trading account? This will clear all virtual positions, orders, and trade history, and restore your capital to <span className="font-bold text-white">₹100,000</span>.
            </p>
            <div className="flex items-center justify-end space-x-3 pt-2">
              <button
                onClick={() => setShowResetModal(false)}
                className="px-4 py-2 bg-surface hover:bg-border text-white text-xs font-bold rounded-lg"
              >
                Cancel
              </button>
              <button
                onClick={async () => {
                  await onResetAccount();
                  setShowResetModal(false);
                }}
                className="px-4 py-2 bg-red-600 hover:bg-red-500 text-white text-xs font-bold rounded-lg shadow-lg shadow-red-600/20"
              >
                Confirm Reset
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
