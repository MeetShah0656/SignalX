'use client';

import React, { useState } from 'react';
import { History, Search, Filter, Trash2 } from 'lucide-react';

interface TradeHistoryViewProps {
  trades: any[];
  onRefresh?: () => void;
}

export const TradeHistoryView: React.FC<TradeHistoryViewProps> = ({ trades, onRefresh }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterReason, setFilterReason] = useState('ALL');

  const handleDeleteTrade = async (tradeId: string) => {
    try {
      await fetch(`/api/trading/trades/${tradeId}`, { method: 'DELETE' });
      if (onRefresh) onRefresh();
    } catch (e) {
      console.error(e);
    }
  };

  const filteredTrades = (trades || []).filter((t) => {
    const matchesSearch = t.symbol?.toLowerCase().includes(searchTerm.toLowerCase()) || t.trade_id?.includes(searchTerm);
    const matchesFilter = filterReason === 'ALL' || t.exit_reason === filterReason;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center space-x-2">
            <History className="w-5 h-5 text-blue-400" />
            <span>Virtual Trade History & Logs</span>
          </h2>
          <p className="text-xs text-textMuted mt-1">Audit log of all executed virtual paper trades.</p>
        </div>

        {/* Filters */}
        <div className="flex items-center space-x-3">
          <div className="relative">
            <Search className="w-4 h-4 text-textMuted absolute left-3 top-2.5" />
            <input
              type="text"
              placeholder="Search Trade ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="bg-card border border-border rounded-lg pl-9 pr-3 py-1.5 text-xs text-white placeholder-textMuted focus:outline-none focus:border-primary w-48"
            />
          </div>

          <select
            value={filterReason}
            onChange={(e) => setFilterReason(e.target.value)}
            className="bg-card border border-border rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:border-primary font-mono"
          >
            <option value="ALL">All Exit Reasons</option>
            <option value="TARGET_HIT">TARGET_HIT</option>
            <option value="STOP_LOSS">STOP_LOSS</option>
            <option value="MANUAL_EXIT">MANUAL_EXIT</option>
          </select>
        </div>
      </div>

      {/* Trade Log Table */}
      <div className="bg-card border border-border rounded-xl p-6">
        {filteredTrades.length === 0 ? (
          <div className="p-8 text-center text-textMuted text-xs bg-surface border border-border rounded-xl">
            No virtual trade records found matching filter criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-surface text-textMuted font-sans uppercase border-b border-border">
                <tr>
                  <th className="p-3">Trade ID</th>
                  <th className="p-3">Side</th>
                  <th className="p-3">Entry Price</th>
                  <th className="p-3 text-blue-400">Realized Exit Price</th>
                  <th className="p-3">Net P&L</th>
                  <th className="p-3">P&L %</th>
                  <th className="p-3">Duration</th>
                  <th className="p-3">Exit Reason</th>
                  <th className="p-3">Model</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredTrades.map((t) => (
                  <tr key={t.trade_id} className="hover:bg-surface/50">
                    <td className="p-3 text-textMuted text-[11px]">{t.trade_id.slice(0, 8)}...</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded font-bold ${t.side === 'LONG' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'}`}>
                        {t.side}
                      </span>
                    </td>
                    <td className="p-3 text-white">₹{t.entry_price.toFixed(2)}</td>
                    <td className="p-3 text-white">₹{t.exit_price.toFixed(2)}</td>
                    <td className={`p-3 font-bold ${t.net_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {t.net_pnl >= 0 ? '+' : ''}₹{t.net_pnl.toFixed(2)}
                    </td>
                    <td className={`p-3 font-bold ${t.pnl_percent >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {t.pnl_percent >= 0 ? '+' : ''}{t.pnl_percent.toFixed(2)}%
                    </td>
                    <td className="p-3 text-textMuted">{Math.round(t.duration_seconds || 0)}s</td>
                    <td className="p-3">
                      <span className="bg-surface border border-border px-2 py-0.5 rounded text-[11px] text-textMuted font-sans">
                        {t.exit_reason}
                      </span>
                    </td>
                    <td className="p-3 text-blue-400 font-bold">{t.model_version}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
