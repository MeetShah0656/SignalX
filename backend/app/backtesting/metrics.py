import numpy as np
import pandas as pd
from typing import Dict, Any, List

def calculate_backtest_metrics(
    trades: List[Dict[str, Any]],
    initial_capital: float,
    equity_curve: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Calculate quantitative trading metrics."""
    if not trades or not equity_curve:
        return {
            "total_return": 0.0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "max_drawdown": 0.0,
            "sharpe_ratio": 0.0,
            "sortino_ratio": 0.0,
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "average_win": 0.0,
            "average_loss": 0.0,
            "cagr": 0.0
        }

    df_trades = pd.DataFrame(trades)
    final_equity = equity_curve[-1]["equity"]
    total_return = (final_equity - initial_capital) / initial_capital * 100.0

    wins = df_trades[df_trades['net_pnl'] > 0]
    losses = df_trades[df_trades['net_pnl'] < 0]

    winning_trades = len(wins)
    losing_trades = len(losses)
    total_trades = len(df_trades)

    win_rate = (winning_trades / total_trades * 100.0) if total_trades > 0 else 0.0

    gross_profit = wins['net_pnl'].sum() if not wins.empty else 0.0
    gross_loss = abs(losses['net_pnl'].sum()) if not losses.empty else 0.0

    profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (gross_profit if gross_profit > 0 else 0.0)

    average_win = wins['net_pnl'].mean() if not wins.empty else 0.0
    average_loss = losses['net_pnl'].mean() if not losses.empty else 0.0

    # Drawdown calculation
    equity_series = pd.Series([e['equity'] for e in equity_curve])
    running_max = equity_series.cummax()
    drawdown = (equity_series - running_max) / running_max * 100.0
    max_drawdown = abs(drawdown.min()) if not drawdown.empty else 0.0

    # Sharpe & Sortino calculation
    returns = equity_series.pct_change().dropna()
    mean_ret = returns.mean()
    std_ret = returns.std()
    downside_std = returns[returns < 0].std()

    sharpe_ratio = (mean_ret / std_ret * np.sqrt(252)) if std_ret > 0 else 0.0
    sortino_ratio = (mean_ret / downside_std * np.sqrt(252)) if downside_std > 0 else 0.0

    return {
        "initial_capital": round(initial_capital, 2),
        "final_equity": round(final_equity, 2),
        "total_return": round(total_return, 2),
        "win_rate": round(win_rate, 2),
        "profit_factor": round(profit_factor, 2),
        "max_drawdown": round(max_drawdown, 2),
        "sharpe_ratio": round(sharpe_ratio, 2),
        "sortino_ratio": round(sortino_ratio, 2),
        "total_trades": total_trades,
        "winning_trades": winning_trades,
        "losing_trades": losing_trades,
        "average_win": round(average_win, 2),
        "average_loss": round(average_loss, 2)
    }
