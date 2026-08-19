'use client';

import React from 'react';
import { 
  TrendingUp, 
  Activity, 
  PlaySquare, 
  History, 
  BarChart3, 
  SlidersHorizontal, 
  BrainCircuit, 
  Settings, 
  ShieldAlert 
} from 'lucide-react';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  systemStatus: any;
  portfolio: any;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  systemStatus,
  portfolio
}) => {
  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: TrendingUp },
    { id: 'live_market', label: 'Live Market', icon: Activity },
    { id: 'paper_trading', label: 'Paper Trading', icon: PlaySquare },
    { id: 'history', label: 'Trade History', icon: History },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'backtesting', label: 'Backtesting', icon: SlidersHorizontal },
    { id: 'ai_model', label: 'AI Model', icon: BrainCircuit },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <header className="bg-surface border-b border-border text-white sticky top-0 z-50">
      {/* Demo / System Status Banner */}
      <div className="bg-blue-950/60 border-b border-blue-800/40 px-4 py-1.5 text-xs flex items-center justify-between text-blue-200">
        <div className="flex items-center space-x-3">
          <span className="bg-blue-600 text-white font-bold px-2 py-0.5 rounded text-[10px] tracking-wider uppercase">
            SIMULATED PAPER TRADING MODE
          </span>
          <span>Zero Real Money Execution • Strictly Paper Trading</span>
        </div>
        <div className="flex items-center space-x-4">
          <span className="flex items-center space-x-1.5">
            <span className={`w-2 h-2 rounded-full ${systemStatus?.market_api === 'CONNECTED' ? 'bg-emerald-400' : 'bg-red-400'}`} />
            <span>{systemStatus?.market_api === 'CONNECTED' ? 'LIVE DATA CONNECTED' : 'DATA DISCONNECTED'}</span>
          </span>
          <span className="flex items-center space-x-1.5">
            <span className={`w-2 h-2 rounded-full ${systemStatus?.ml_model === 'READY' ? 'bg-emerald-400' : 'bg-amber-400'}`} />
            <span>{systemStatus?.ml_model === 'READY' ? 'AI MODEL READY' : 'MODEL NOT TRAINED'}</span>
          </span>
          <span className="flex items-center space-x-1.5 font-mono text-emerald-400">
            <span>Equity: ₹{portfolio?.equity ? portfolio.equity.toLocaleString('en-IN') : '1,00,000'}</span>
          </span>
        </div>
      </div>

      {/* Main Nav Bar */}
      <div className="max-w-7xl mx-auto px-4 flex items-center justify-between h-16">
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('dashboard')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
            <TrendingUp className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
              SignalX
            </h1>
            <p className="text-[10px] text-textMuted tracking-wider font-semibold uppercase">AI NIFTY Quantitative Engine</p>
          </div>
        </div>

        {/* Tab Links */}
        <nav className="flex items-center space-x-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-primary text-white shadow-md shadow-primary/20'
                    : 'text-textMuted hover:text-white hover:bg-card'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
