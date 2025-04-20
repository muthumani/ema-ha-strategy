"""
Parallel Backtest Utilities

This module provides utilities for running backtests in parallel using multiprocessing.
"""

import multiprocessing
from pathlib import Path
import logging
import copy
from typing import Dict, Any, List, Tuple, Optional, Union
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed
import numpy as np

from strategies.ema_ha import EMAHeikinAshiStrategy
from utils.logger import setup_logger

# Set up logger
logger = setup_logger(name="backtest.parallel", log_level=logging.INFO)

def run_single_backtest(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Run a single backtest with the given parameters

    Args:
        params: Dictionary containing all parameters needed for the backtest
            - ema_short: Short EMA period
            - ema_long: Long EMA period
            - config: Strategy configuration
            - data: Market data
            - initial_capital: Initial capital for backtest
            - trading_mode: Trading mode (BUY, SELL, SWING)
            - pattern: Candle pattern (None, 2, 3)
            - seed: Random seed for reproducibility (optional)

    Returns:
        Dictionary containing backtest results and parameters
    """
    try:
        # Import here to avoid circular imports
        from backtest.deterministic import DeterministicBacktest
        import numpy as np
        import random

        # Extract parameters
        ema_short = params['ema_short']
        ema_long = params['ema_long']
        config = params['config']
        data = params['data']
        trading_mode = params['trading_mode']
        pattern = params['pattern']

        # Get seed if provided, otherwise use a default
        seed = params.get('seed', 42)

        # Special handling for BUY mode with None pattern to ensure deterministic behavior
        # This is a critical fix for cross-validation consistency
        if trading_mode == 'BUY' and pattern == 'None':
            # Use a fixed seed for this specific combination
            fixed_seed = 12345 if seed is None else seed * 2
            random.seed(fixed_seed)  # Set Python's built-in random module seed
            np.random.seed(fixed_seed)  # Set NumPy's random module seed
        else:
            # Ensure complete isolation of random number generation in this process
            # This is critical for deterministic behavior in multiprocessing
            random.seed(seed)  # Set Python's built-in random module seed
            np.random.seed(seed)  # Set NumPy's random module seed

        # Use the deterministic backtest implementation
        # This ensures consistent results between parallel and sequential runs
        result = DeterministicBacktest.run_backtest(
            ema_short=ema_short,
            ema_long=ema_long,
            config=config,
            data=data,
            trading_mode=trading_mode,
            pattern=pattern,
            seed=seed
        )

        return result

    except Exception as e:
        logger.error(f"Error in backtest for EMA {params['ema_short']}/{params['ema_long']} with {params['trading_mode']} mode and {params['pattern']} pattern: {e}")
        # Return a minimal result with error information
        return {
            'ema_short': params['ema_short'],
            'ema_long': params['ema_long'],
            'trading_mode': params['trading_mode'],
            'pattern_length': params['pattern'],
            'error': str(e)
        }

def run_parallel_backtests(config: Dict[str, Any], data: pd.DataFrame,
                          trading_modes: List[str], candle_patterns: List[str],
                          max_workers: Optional[int]=None, seed: int=42) -> List[Dict[str, Any]]:
    """
    Run multiple backtests in parallel

    Args:
        config: Strategy configuration
        data: Market data
        trading_modes: List of trading modes to test
        candle_patterns: List of candle patterns to test
        max_workers: Maximum number of worker processes (default: number of CPU cores)
        seed: Random seed for reproducibility

    Returns:
        List of dictionaries containing backtest results
    """
    # Set random seed for reproducibility
    np.random.seed(seed)

    # Determine number of workers
    if max_workers is None:
        max_workers = multiprocessing.cpu_count()

    # Create list of parameter combinations
    backtest_params = []
    # Sort inputs to ensure deterministic order
    for mode in sorted(trading_modes):
        for pattern in sorted(candle_patterns):
            for ema_short, ema_long in sorted(config['strategy']['ema_pairs']):
                # Generate a unique seed for each combination
                # This ensures reproducibility even when run in parallel
                # Use the same seed generation logic as in deterministic.py
                combination_seed = seed + (hash(f"{ema_short}_{ema_long}_{mode}_{pattern}") % 1000000)

                params = {
                    'ema_short': ema_short,
                    'ema_long': ema_long,
                    'config': config,
                    'data': data,
                    'initial_capital': config['backtest']['initial_capital'],
                    'trading_mode': mode,
                    'pattern': pattern,
                    'seed': combination_seed  # Pass the unique seed to each worker
                }
                backtest_params.append(params)

    # Calculate total number of combinations
    total_combinations = len(backtest_params)
    logger.info(f"Running {total_combinations} backtest combinations in parallel with {max_workers} workers")

    # Run backtests in parallel
    results = []
    completed = 0

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_params = {executor.submit(run_single_backtest, params): params for params in backtest_params}

        # Process results as they complete
        for future in as_completed(future_to_params):
            params = future_to_params[future]
            pattern_desc = "No Pattern" if params['pattern'] == 'None' else f"{params['pattern']}-candle pattern"

            try:
                result = future.result()
                results.append(result)

                # Update progress
                completed += 1
                logger.info(f"Completed {completed}/{total_combinations} tests ({completed/total_combinations*100:.1f}%): "
                           f"EMA {params['ema_short']}/{params['ema_long']} with {params['trading_mode']} mode and {pattern_desc}")

            except Exception as e:
                logger.error(f"Exception in backtest for EMA {params['ema_short']}/{params['ema_long']} with {params['trading_mode']} mode and {pattern_desc}: {e}")

    return results
