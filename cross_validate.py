#!/usr/bin/env python
"""
Cross-Validation Script for Backtest Results

This script runs both sequential and parallel implementations with the same seed
and compares the results to ensure they are identical.
"""

import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
import logging
import argparse
import time
from typing import Dict, Any, List, Tuple

from backtest_utils import load_config, load_data
from strategies.ema_ha import EMAHeikinAshiStrategy
from utils.parallel_backtest import run_parallel_backtests
from logger import setup_logger

# Set up logger
logger = setup_logger(name="cross_validator", log_level=logging.INFO)

def run_sequential_backtest(config: Dict[str, Any], data: pd.DataFrame, 
                           trading_modes: List[str], candle_patterns: List[str],
                           seed: int = 42) -> List[Dict[str, Any]]:
    """
    Run backtests sequentially with a fixed seed
    
    Args:
        config: Strategy configuration
        data: Market data
        trading_modes: List of trading modes to test
        candle_patterns: List of candle patterns to test
        seed: Random seed for reproducibility
        
    Returns:
        List of dictionaries containing backtest results
    """
    # Set random seed for reproducibility
    np.random.seed(seed)
    
    # Store results for all combinations
    all_combination_results = []
    
    # Run all combinations
    total_combinations = len(trading_modes) * len(candle_patterns) * len(config['strategy']['ema_pairs'])
    completed = 0
    
    start_time = time.time()
    logger.info(f"Running {total_combinations} backtest combinations sequentially")
    
    for mode in trading_modes:
        for pattern in candle_patterns:
            # Create a copy of config with this mode and pattern
            mode_pattern_config = config.copy()
            
            # Set trading mode
            if 'strategy' not in mode_pattern_config:
                mode_pattern_config['strategy'] = {}
            if 'trading' not in mode_pattern_config['strategy']:
                mode_pattern_config['strategy']['trading'] = {}
            mode_pattern_config['strategy']['trading']['mode'] = [mode]
            
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
            
            # Run each EMA pair
            for ema_short, ema_long in config['strategy']['ema_pairs']:
                pattern_desc = "No Pattern" if pattern == 'None' else f"{pattern}-candle pattern"
                logger.info(f"Testing EMA {ema_short}/{ema_long} with {mode} mode and {pattern_desc}")
                
                # Initialize strategy
                strategy = EMAHeikinAshiStrategy(ema_short, ema_long, mode_pattern_config)
                
                # Run backtest
                results, _ = strategy.backtest(data, initial_capital=config['backtest']['initial_capital'])
                
                # Add combination info to results
                results['trading_mode'] = mode
                results['pattern_length'] = pattern
                
                # Add to combined results
                all_combination_results.append(results)
                
                # Update progress
                completed += 1
                logger.info(f"Completed {completed}/{total_combinations} tests ({completed/total_combinations*100:.1f}%)")
    
    end_time = time.time()
    logger.info(f"Sequential execution completed in {end_time - start_time:.2f} seconds")
    
    return all_combination_results

def run_parallel_validation(config_path: str, data_path: str = None, seed: int = 42):
    """
    Run both sequential and parallel implementations and compare results
    
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
    data = load_data(data_path)
    
    # Define trading modes and candle patterns
    trading_modes = ['BUY', 'SELL', 'SWING']
    candle_patterns = ['None', '2', '3']
    
    # Create output directory for validation results
    output_dir = Path('data/validation')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Set random seed for reproducibility
    np.random.seed(seed)
    
    # Run sequential implementation
    logger.info("Running sequential implementation...")
    sequential_start = time.time()
    sequential_results = run_sequential_backtest(config, data, trading_modes, candle_patterns, seed)
    sequential_end = time.time()
    sequential_time = sequential_end - sequential_start
    
    # Save sequential results
    with open(output_dir / 'sequential_results.json', 'w') as f:
        json.dump(sequential_results, f, indent=4)
    
    # Reset random seed for parallel implementation
    np.random.seed(seed)
    
    # Run parallel implementation
    logger.info("Running parallel implementation...")
    parallel_start = time.time()
    parallel_results = run_parallel_backtests(config, data, trading_modes, candle_patterns)
    parallel_end = time.time()
    parallel_time = parallel_end - parallel_start
    
    # Save parallel results
    with open(output_dir / 'parallel_results.json', 'w') as f:
        json.dump(parallel_results, f, indent=4)
    
    # Compare results
    logger.info("Comparing results...")
    
    # Sort results for consistent comparison
    sequential_results = sorted(sequential_results, key=lambda x: (x['ema_short'], x['ema_long'], x['trading_mode'], x['pattern_length']))
    parallel_results = sorted(parallel_results, key=lambda x: (x['ema_short'], x['ema_long'], x['trading_mode'], x['pattern_length']))
    
    # Check if results are identical
    identical = True
    differences = []
    
    if len(sequential_results) != len(parallel_results):
        identical = False
        logger.error(f"Different number of results: Sequential={len(sequential_results)}, Parallel={len(parallel_results)}")
    else:
        for i, (seq_result, par_result) in enumerate(zip(sequential_results, parallel_results)):
            # Check key metrics
            key_metrics = ['ema_short', 'ema_long', 'trading_mode', 'pattern_length', 
                          'total_trades', 'win_rate', 'profit_factor', 'total_profit', 
                          'return_pct', 'max_drawdown_pct', 'sharpe_ratio']
            
            for metric in key_metrics:
                if metric in seq_result and metric in par_result:
                    # For numerical values, allow small floating point differences
                    if isinstance(seq_result[metric], (int, float)) and isinstance(par_result[metric], (int, float)):
                        if abs(seq_result[metric] - par_result[metric]) > 1e-6:
                            identical = False
                            differences.append({
                                'combination': f"EMA {seq_result['ema_short']}/{seq_result['ema_long']} with {seq_result['trading_mode']} mode and {seq_result['pattern_length']} pattern",
                                'metric': metric,
                                'sequential': seq_result[metric],
                                'parallel': par_result[metric],
                                'difference': abs(seq_result[metric] - par_result[metric])
                            })
                    # For non-numerical values, require exact match
                    elif seq_result[metric] != par_result[metric]:
                        identical = False
                        differences.append({
                            'combination': f"EMA {seq_result['ema_short']}/{seq_result['ema_long']} with {seq_result['trading_mode']} mode and {seq_result['pattern_length']} pattern",
                            'metric': metric,
                            'sequential': seq_result[metric],
                            'parallel': par_result[metric]
                        })
    
    # Save differences to file
    with open(output_dir / 'differences.json', 'w') as f:
        json.dump(differences, f, indent=4)
    
    # Print summary
    logger.info(f"Sequential execution time: {sequential_time:.2f} seconds")
    logger.info(f"Parallel execution time: {parallel_time:.2f} seconds")
    logger.info(f"Speedup: {sequential_time / parallel_time:.2f}x")
    
    if identical:
        logger.info("VALIDATION PASSED: Sequential and parallel results are identical!")
    else:
        logger.error(f"VALIDATION FAILED: Found {len(differences)} differences between sequential and parallel results")
        logger.error(f"See {output_dir / 'differences.json'} for details")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cross-validate sequential and parallel backtest implementations")
    parser.add_argument("--config", default="config/config.yaml", help="Path to configuration file")
    parser.add_argument("--data", help="Path to market data file (overrides config)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    
    args = parser.parse_args()
    
    run_parallel_validation(args.config, args.data, args.seed)
