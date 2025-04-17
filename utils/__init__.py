"""
Utility functions for the EMA Heikin Ashi strategy.
"""

import yaml
import pandas as pd
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Create output directories if they don't exist
        os.makedirs(config['data']['data_folder'], exist_ok=True)
        os.makedirs(config['data']['results_folder'], exist_ok=True)
        
        return config
    except Exception as e:
        raise ValueError(f"Error loading configuration: {e}")

def load_data(data_path: str) -> pd.DataFrame:
    """
    Load market data from CSV file
    
    Args:
        data_path: Path to market data file
        
    Returns:
        DataFrame with market data
    """
    try:
        # Load data
        df = pd.read_csv(data_path)
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Set date as index
        df.set_index('date', inplace=True)
        
        # Store original file path in attributes
        df.attrs['data_path'] = str(data_path)
        df.attrs['data_loaded'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return df
    except Exception as e:
        raise ValueError(f"Error loading market data: {e}")

def save_results(results: Dict[str, Any], trades: List[Dict[str, Any]], 
                symbol: str, ema_short: int, ema_long: int, data_attrs: Dict[str, Any]) -> None:
    """
    Save backtest results to JSON and CSV files
    
    Args:
        results: Dictionary with backtest results
        trades: List of trade dictionaries
        symbol: Trading symbol
        ema_short: Short EMA period
        ema_long: Long EMA period
        data_attrs: Attributes from the data DataFrame
    """
    try:
        # Create timestamp for filenames
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create results directory if it doesn't exist
        results_dir = Path(results.get('results_dir', 'data/results'))
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Save results to JSON
        results_file = results_dir / f"{symbol}_EMA_{ema_short}_{ema_long}_{timestamp}_results.json"
        
        # Add data attributes to results
        results['data_source'] = data_attrs.get('data_path', 'unknown')
        results['data_loaded'] = data_attrs.get('data_loaded', 'unknown')
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=4)
        
        # Save trades to CSV
        trades_file = results_dir / f"{symbol}_EMA_{ema_short}_{ema_long}_{timestamp}_trades.csv"
        trades_df = pd.DataFrame(trades)
        trades_df.to_csv(trades_file, index=False)
        
        return results_file, trades_file
    except Exception as e:
        raise ValueError(f"Error saving results: {e}")

def calculate_performance_metrics(trades: List[Dict[str, Any]], initial_capital: float) -> Dict[str, Any]:
    """
    Calculate performance metrics from trades
    
    Args:
        trades: List of trade dictionaries
        initial_capital: Initial capital
        
    Returns:
        Dictionary with performance metrics
    """
    try:
        # Calculate basic metrics
        total_trades = len(trades)
        winning_trades = sum(1 for trade in trades if trade['pnl'] > 0)
        losing_trades = total_trades - winning_trades
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # Calculate profit metrics
        total_profit = sum(trade['pnl'] for trade in trades)
        winning_profit = sum(trade['pnl'] for trade in trades if trade['pnl'] > 0)
        losing_profit = sum(trade['pnl'] for trade in trades if trade['pnl'] <= 0)
        
        profit_factor = abs(winning_profit / losing_profit) if losing_profit != 0 else float('inf')
        
        # Calculate return metrics
        return_pct = (total_profit / initial_capital) * 100
        
        # Calculate drawdown
        equity_curve = [initial_capital]
        for trade in trades:
            equity_curve.append(equity_curve[-1] + trade['pnl'])
        
        running_max = pd.Series(equity_curve).cummax()
        drawdowns = (running_max - equity_curve) / running_max * 100
        max_drawdown = drawdowns.max()
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'winning_profit': winning_profit,
            'losing_profit': losing_profit,
            'profit_factor': profit_factor,
            'return_pct': return_pct,
            'max_drawdown_pct': max_drawdown
        }
    except Exception as e:
        raise ValueError(f"Error calculating performance metrics: {e}")
