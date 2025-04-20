"""
Backtesting package for the EMA Heikin Ashi strategy.

This package contains modules for backtesting, validation, and cross-validation.
"""

# Import key functions for easier access
from backtest.utils import load_config, load_data, save_results
from backtest.deterministic import DeterministicBacktest
from backtest.parallel import run_parallel_backtests
