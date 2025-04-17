#!/usr/bin/env python
"""
Deterministic Backtest Module

This module provides a wrapper around the EMAHeikinAshiStrategy to ensure
deterministic results regardless of execution method (sequential or parallel).
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional, Union
import copy
import logging
from pathlib import Path

from strategies.ema_ha import EMAHeikinAshiStrategy
from logger import setup_logger

# Set up logger
logger = setup_logger(name="deterministic_backtest", log_level=logging.INFO)

class DeterministicBacktest:
    """
    A wrapper class that ensures deterministic backtest results
    by controlling random seed and execution flow.
    """
    
    @staticmethod
    def run_backtest(
        ema_short: int,
        ema_long: int,
        config: Dict[str, Any],
        data: pd.DataFrame,
        trading_mode: str,
        pattern: str,
        seed: int = 42
    ) -> Dict[str, Any]:
        """
        Run a single backtest with deterministic results
        
        Args:
            ema_short: Short EMA period
            ema_long: Long EMA period
            config: Strategy configuration
            data: Market data
            trading_mode: Trading mode (BUY, SELL, SWING)
            pattern: Candle pattern (None, 2, 3)
            seed: Random seed for reproducibility
            
        Returns:
            Dictionary containing backtest results
        """
        # Set random seed for reproducibility
        np.random.seed(seed)
        
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
        results, _ = strategy.backtest(data, initial_capital=config['backtest']['initial_capital'])
        
        # Add combination info to results
        results['trading_mode'] = trading_mode
        results['pattern_length'] = pattern
        
        return results
    
    @staticmethod
    def run_all_combinations(
        config: Dict[str, Any],
        data: pd.DataFrame,
        trading_modes: List[str],
        candle_patterns: List[str],
        seed: int = 42
    ) -> List[Dict[str, Any]]:
        """
        Run all combinations of trading modes, candle patterns, and EMA pairs
        
        Args:
            config: Strategy configuration
            data: Market data
            trading_modes: List of trading modes to test
            candle_patterns: List of candle patterns to test
            seed: Random seed for reproducibility
            
        Returns:
            List of dictionaries containing backtest results
        """
        # Set master random seed
        np.random.seed(seed)
        
        # Store results for all combinations
        all_results = []
        
        # Calculate total combinations
        total_combinations = len(trading_modes) * len(candle_patterns) * len(config['strategy']['ema_pairs'])
        completed = 0
        
        # Run all combinations in a deterministic order
        for mode in sorted(trading_modes):
            for pattern in sorted(candle_patterns):
                for ema_short, ema_long in sorted(config['strategy']['ema_pairs']):
                    # Generate a unique seed for each combination
                    # This ensures reproducibility even when run in parallel
                    combination_seed = seed + (hash(f"{ema_short}_{ema_long}_{mode}_{pattern}") % 1000000)
                    
                    # Run backtest with the unique seed
                    result = DeterministicBacktest.run_backtest(
                        ema_short=ema_short,
                        ema_long=ema_long,
                        config=config,
                        data=data,
                        trading_mode=mode,
                        pattern=pattern,
                        seed=combination_seed
                    )
                    
                    # Add to results
                    all_results.append(result)
                    
                    # Update progress
                    completed += 1
                    logger.info(f"Completed {completed}/{total_combinations} tests ({completed/total_combinations*100:.1f}%)")
        
        return all_results
