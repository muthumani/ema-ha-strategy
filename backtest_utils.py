import pandas as pd
import numpy as np
import yaml
from pathlib import Path
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Union, Optional, Tuple
import logging
from logger import setup_logger

# Set up logger
logger = setup_logger(name="backtest_utils", log_level=logging.INFO)

def load_config(config_path: str = 'config/config.yaml') -> Dict[str, Any]:
    """
    Load configuration from yaml file

    Args:
        config_path: Path to the configuration file

    Returns:
        Dictionary containing configuration settings

    Raises:
        FileNotFoundError: If the config file doesn't exist
        yaml.YAMLError: If the config file has invalid YAML syntax
    """
    try:
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Validate essential configuration keys
        required_keys = ['strategy', 'backtest', 'data']
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required configuration section: {key}")

        logger.info(f"Configuration loaded successfully from {config_path}")
        return config

    except FileNotFoundError as e:
        logger.error(f"Config file not found: {e}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading configuration: {e}")
        raise

def load_data(file_path: Union[str, Path]) -> pd.DataFrame:
    """
    Load market data from CSV file and ensure it's sorted by datetime

    Args:
        file_path: Path to the CSV file containing market data

    Returns:
        DataFrame with market data indexed by datetime

    Raises:
        FileNotFoundError: If the data file doesn't exist
        ValueError: If the data file is empty or missing required columns
    """
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file not found: {file_path}")

        logger.info(f"Loading market data from {file_path}")

        # Read CSV file
        df = pd.read_csv(file_path)

        if df.empty:
            raise ValueError(f"Data file is empty: {file_path}")

        # Check for required columns
        required_columns = ['date', 'open', 'high', 'low', 'close']
        missing_columns = [col for col in required_columns if col.lower() not in [c.lower() for c in df.columns]]

        if missing_columns:
            raise ValueError(f"Missing required columns in data file: {missing_columns}")

        # Convert column names to lowercase for consistency
        df.columns = df.columns.str.lower()

        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])

        logger.debug(f"Data before sorting - First row: {df['date'].iloc[0]}, Last row: {df['date'].iloc[-1]}")

        # Sort by datetime (ensuring both date and time are considered)
        df = df.sort_values('date', ascending=True)

        logger.debug(f"Data after sorting - First row: {df['date'].iloc[0]}, Last row: {df['date'].iloc[-1]}")

        # Verify sorting
        if not df['date'].is_monotonic_increasing:
            logger.warning("Data is not properly sorted after sorting operation!")
            # Show a few examples where sorting is incorrect
            for i in range(len(df)-1):
                if df['date'].iloc[i] > df['date'].iloc[i+1]:
                    logger.warning(f"Sorting issue at index {i}: {df['date'].iloc[i]} > {df['date'].iloc[i+1]}")
                    break

        # Set datetime as index
        df.set_index('date', inplace=True)

        # Store date range info in the DataFrame attributes
        df.attrs['start_date'] = df.index.min().strftime('%Y-%m-%d %H:%M:%S')
        df.attrs['end_date'] = df.index.max().strftime('%Y-%m-%d %H:%M:%S')
        # Convert index.date to Series before using unique()
        df.attrs['total_days'] = len(pd.Series(df.index.date).unique())
        df.attrs['total_candles'] = len(df)

        logger.info(f"Data loaded successfully - {df.attrs['total_candles']} candles from {df.attrs['start_date']} to {df.attrs['end_date']}")

        return df

    except FileNotFoundError as e:
        logger.error(f"Data file not found: {e}")
        raise
    except pd.errors.EmptyDataError:
        logger.error(f"Empty data file: {file_path}")
        raise ValueError(f"Data file is empty: {file_path}")
    except pd.errors.ParserError as e:
        logger.error(f"Error parsing CSV file: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error loading data: {e}")
        raise

def save_results(
    results: Dict[str, Any],
    trades: List[Dict[str, Any]],
    symbol: str,
    ema_short: int,
    ema_long: int,
    data_attrs: Dict[str, Any]
) -> Tuple[Path, Path]:
    """
    Save backtest results and trades with date range information

    Args:
        results: Dictionary containing backtest results
        trades: List of trade dictionaries
        symbol: Trading symbol (e.g., 'NIFTY')
        ema_short: Short EMA period
        ema_long: Long EMA period
        data_attrs: Data attributes containing date range information

    Returns:
        Tuple of (results_file_path, trades_file_path)

    Raises:
        IOError: If there's an error writing the files
    """
    try:
        # Create results directory if it doesn't exist
        results_dir = Path('data/results')
        results_dir.mkdir(parents=True, exist_ok=True)

        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{symbol}_EMA_{ema_short}_{ema_long}_{timestamp}"

        # Add date range information to results
        results.update({
            'backtest_period': {
                'start_date': data_attrs['start_date'],
                'end_date': data_attrs['end_date'],
                'total_trading_days': data_attrs['total_days'],
                'total_candles': data_attrs['total_candles']
            }
        })

        # Save results
        results_file = results_dir / f"{filename}_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=4)

        # Save trades
        trades_file = results_dir / f"{filename}_trades.csv"
        trades_df = pd.DataFrame(trades)
        trades_df.to_csv(trades_file, index=False)

        logger.info(f"Results saved to {results_file}")
        logger.info(f"Trades saved to {trades_file}")

        return results_file, trades_file

    except IOError as e:
        logger.error(f"Error saving results: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error saving results: {e}")
        raise

def calculate_performance_metrics(
    trades: List[Dict[str, Any]],
    initial_capital: float
) -> Dict[str, Any]:
    """
    Calculate comprehensive performance metrics from trade list

    NOTE: This function is currently unused as EMAHeikinAshiStrategy.backtest()
    calculates metrics directly. Kept for future enhancement to provide a centralized
    metrics calculation that could be used across different strategy implementations.

    Args:
        trades: List of trade dictionaries
        initial_capital: Initial capital amount

    Returns:
        Dictionary containing performance metrics
    """
    if not trades:
        return {
            'total_trades': 0,
            'win_rate': 0.0,
            'profit_factor': 0.0,
            'total_profit': 0.0,
            'return_pct': 0.0,
            'max_drawdown_pct': 0.0,
            'sharpe_ratio': 0.0,
            'avg_trade_duration': 0.0
        }

    # Extract basic metrics
    total_trades = len(trades)
    winning_trades = sum(1 for t in trades if t['pnl'] > 0)
    win_rate = winning_trades / total_trades if total_trades > 0 else 0

    # Calculate profit metrics
    total_profit = sum(t['pnl'] for t in trades)
    return_pct = (total_profit / initial_capital) * 100

    # Calculate profit factor
    gross_profit = sum(t['pnl'] for t in trades if t['pnl'] > 0)
    gross_loss = abs(sum(t['pnl'] for t in trades if t['pnl'] <= 0))
    profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')

    # Calculate drawdown
    equity_curve = [initial_capital]
    for trade in trades:
        equity_curve.append(equity_curve[-1] + trade['pnl'])

    peak = initial_capital
    drawdowns = []

    for equity in equity_curve:
        if equity > peak:
            peak = equity
        drawdown_pct = (peak - equity) / peak * 100 if peak > 0 else 0
        drawdowns.append(drawdown_pct)

    max_drawdown_pct = max(drawdowns) if drawdowns else 0

    # Calculate average trade duration
    avg_duration = sum(t['duration'] for t in trades) / total_trades if total_trades > 0 else 0

    # Group trades by month for monthly returns
    monthly_returns = {}
    for trade in trades:
        month = trade['entry_time'][:7]  # Extract YYYY-MM
        if month not in monthly_returns:
            monthly_returns[month] = 0
        monthly_returns[month] += trade['pnl']

    monthly_returns_arr = np.array(list(monthly_returns.values()))
    monthly_returns_pct = monthly_returns_arr / initial_capital * 100

    # Calculate Sharpe ratio (assuming risk-free rate of 0)
    sharpe_ratio = np.mean(monthly_returns_pct) / np.std(monthly_returns_pct) if np.std(monthly_returns_pct) > 0 else 0

    return {
        'total_trades': total_trades,
        'winning_trades': winning_trades,
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'total_profit': total_profit,
        'return_pct': return_pct,
        'max_drawdown_pct': max_drawdown_pct,
        'sharpe_ratio': sharpe_ratio,
        'avg_trade_duration': avg_duration,
        'monthly_returns_avg': float(np.mean(monthly_returns_pct)),
        'monthly_returns_std': float(np.std(monthly_returns_pct)),
        'profitable_months': float(np.sum(monthly_returns_pct > 0)),
        'max_monthly_profit': float(np.max(monthly_returns_pct)) if len(monthly_returns_pct) > 0 else 0,
        'max_monthly_loss': float(np.min(monthly_returns_pct)) if len(monthly_returns_pct) > 0 else 0
    }
