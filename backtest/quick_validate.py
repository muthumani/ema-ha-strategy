"""
Quick Validation Script

This script runs a quick validation test with a small subset of combinations
to verify that sequential and parallel implementations produce identical results.
"""

import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
import logging
import argparse
import time
import copy
from typing import Dict, Any, List, Tuple

from backtest.utils import load_config, load_data
from strategies.ema_ha import EMAHeikinAshiStrategy
from backtest.deterministic import DeterministicBacktest
from utils.logger import setup_logger

# Set up logger
logger = setup_logger(name="backtest.quick_validator", log_level=logging.INFO)

def run_quick_validation(config_path: str, data_path: str = None, seed: int = 42):
    """
    Run a quick validation test with a small subset of combinations

    Args:
        config_path: Path to configuration file
        data_path: Path to market data file (overrides config)
        seed: Random seed for reproducibility
    """
    # Load configuration
    config = load_config(config_path)

    # Load data
    if not data_path:
        data_folder = config['data']['data_folder']
        symbol = 'NIFTY'  # Default symbol
        data_path = Path(data_folder) / f"{symbol}_{config['data']['timeframe']}.csv"

    logger.info(f"Loading market data from {data_path}")
    data = load_data(data_path)

    # Create output directory for validation results
    output_dir = Path('data/validation')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Define a small subset of test parameters
    # Just test one EMA pair with one trading mode and one pattern
    ema_short = 13
    ema_long = 34
    trading_mode = 'BUY'
    pattern = 'None'

    logger.info(f"Running quick validation test for EMA {ema_short}/{ema_long} with {trading_mode} mode and {pattern} pattern")

    # Set random seed for reproducibility
    np.random.seed(seed)

    # Run sequential test
    logger.info("Running sequential test...")
    sequential_start = time.time()

    # Create a copy of config with this mode and pattern
    mode_pattern_config = copy.deepcopy(config)

    # Set trading mode
    if 'strategy' not in mode_pattern_config:
        mode_pattern_config['strategy'] = {}
    if 'trading' not in mode_pattern_config['strategy']:
        mode_pattern_config['strategy']['trading'] = {}
    mode_pattern_config['strategy']['trading']['mode'] = [trading_mode]

    # Set candle pattern
    if 'ha_patterns' not in mode_pattern_config['strategy']:
        mode_pattern_config['strategy']['ha_patterns'] = {}

    if pattern == 'None':
        # For 'None' pattern, set confirmation_candles to [None] to indicate
        # no additional filtering but still keep basic HA candle conditions
        mode_pattern_config['strategy']['ha_patterns']['confirmation_candles'] = [None]
    else:
        # Use specified pattern length
        mode_pattern_config['strategy']['ha_patterns']['confirmation_candles'] = [int(pattern)]

    # Initialize strategy
    strategy = EMAHeikinAshiStrategy(ema_short, ema_long, mode_pattern_config)

    # Run backtest
    sequential_result, _ = strategy.backtest(data, initial_capital=config['backtest']['initial_capital'])

    # Add combination info to results
    sequential_result['trading_mode'] = trading_mode
    sequential_result['pattern_length'] = pattern

    sequential_end = time.time()
    sequential_time = sequential_end - sequential_start

    # Save sequential result
    with open(output_dir / 'sequential_quick_result.json', 'w') as f:
        json.dump(sequential_result, f, indent=4)

    # Reset random seed for deterministic test
    np.random.seed(seed)

    # Run deterministic test
    logger.info("Running deterministic test...")
    deterministic_start = time.time()
    deterministic_result = DeterministicBacktest.run_backtest(
        ema_short=ema_short,
        ema_long=ema_long,
        config=config,
        data=data,
        trading_mode=trading_mode,
        pattern=pattern,
        seed=seed
    )
    deterministic_end = time.time()
    deterministic_time = deterministic_end - deterministic_start

    # Save deterministic result
    with open(output_dir / 'deterministic_quick_result.json', 'w') as f:
        json.dump(deterministic_result, f, indent=4)

    # Compare results
    logger.info("Comparing results...")

    # Check if results are identical
    identical = True
    differences = []

    # Check key metrics
    key_metrics = ['ema_short', 'ema_long', 'trading_mode', 'pattern_length',
                  'total_trades', 'win_rate', 'profit_factor', 'total_profit',
                  'return_pct', 'max_drawdown_pct', 'sharpe_ratio']

    for metric in key_metrics:
        if metric in sequential_result and metric in deterministic_result:
            # For numerical values, allow small floating point differences
            if isinstance(sequential_result[metric], (int, float)) and isinstance(deterministic_result[metric], (int, float)):
                if abs(sequential_result[metric] - deterministic_result[metric]) > 1e-6:
                    identical = False
                    differences.append({
                        'metric': metric,
                        'sequential': sequential_result[metric],
                        'deterministic': deterministic_result[metric],
                        'difference': abs(sequential_result[metric] - deterministic_result[metric])
                    })
            # For non-numerical values, require exact match
            elif sequential_result[metric] != deterministic_result[metric]:
                identical = False
                differences.append({
                    'metric': metric,
                    'sequential': sequential_result[metric],
                    'deterministic': deterministic_result[metric]
                })

    # Save differences to file
    with open(output_dir / 'quick_differences.json', 'w') as f:
        json.dump(differences, f, indent=4)

    # Print summary
    logger.info(f"Sequential execution time: {sequential_time:.2f} seconds")
    logger.info(f"Deterministic execution time: {deterministic_time:.2f} seconds")

    if identical:
        logger.info("VALIDATION PASSED: Sequential and deterministic results are identical!")
    else:
        logger.error(f"VALIDATION FAILED: Found {len(differences)} differences between sequential and deterministic results")
        logger.error(f"See {output_dir / 'quick_differences.json'} for details")

    # Print recommendation
    if identical:
        logger.info("\nRECOMMENDATION: The deterministic implementation produces identical results to the sequential implementation.")
        logger.info("You can safely use the parallel implementation with the deterministic backtest for faster execution.")
    else:
        logger.error("\nRECOMMENDATION: The deterministic implementation does NOT produce identical results to the sequential implementation.")
        logger.error("Further investigation is needed to ensure consistent results.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Quick validation of sequential and deterministic backtest implementations")
    parser.add_argument("--config", default="config/config.yaml", help="Path to configuration file")
    parser.add_argument("--data", help="Path to market data file (overrides config)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")

    args = parser.parse_args()

    run_quick_validation(args.config, args.data, args.seed)
