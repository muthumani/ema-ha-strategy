"""
Integration tests for the EMA Heikin Ashi strategy.
"""

import pytest
import os
import tempfile
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import yaml
import json
from pathlib import Path

import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from strategies.ema_ha import EMAHeikinAshiStrategy
from backtest.utils import load_config, load_data, save_results
from utils.config_validator import validate_config

# Create sample data for testing
def create_sample_data(periods=100):
    """Create sample market data for testing"""
    start_date = datetime(2023, 1, 1, 9, 15)
    dates = [start_date + timedelta(minutes=i) for i in range(periods)]

    # Create a simple uptrend followed by a downtrend
    close_prices = []
    for i in range(periods):
        if i < periods // 2:
            # Uptrend with some noise
            price = 100 + i * 0.5 + np.random.normal(0, 0.2)
        else:
            # Downtrend with some noise
            price = 100 + (periods // 2) * 0.5 - (i - periods // 2) * 0.3 + np.random.normal(0, 0.2)
        close_prices.append(price)

    # Create OHLC data
    data = pd.DataFrame({
        'date': dates,
        'open': close_prices,
        'high': [p + np.random.uniform(0.1, 0.5) for p in close_prices],
        'low': [p - np.random.uniform(0.1, 0.5) for p in close_prices],
        'close': close_prices,
        'volume': [np.random.randint(1000, 5000) for _ in range(periods)]
    })

    return data

# Sample configuration for testing
SAMPLE_CONFIG = {
    "strategy": {
        "ema_pairs": [[5, 10], [8, 16]],  # Use shorter periods for testing
        "trading": {
            "mode": ["SWING"]
        },
        "ha_patterns": {
            "enabled": True,
            "confirmation_candles": [2]
        },
        "trading_session": {
            "market_open": "09:15",
            "market_entry": "09:30",
            "force_exit": "15:15",
            "market_close": "15:30"
        }
    },
    "backtest": {
        "initial_capital": 10000,
        "commission": 0.0,
        "slippage": 0.0
    },
    "data": {
        "data_folder": "data/market_data",
        "results_folder": "data/results",
        "timeframe": "1min"
    },
    "logging": {
        "level": "INFO"
    }
}

@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file"""
    with tempfile.NamedTemporaryFile(suffix='.yaml', mode='w', delete=False, encoding='utf-8') as temp:
        yaml.dump(SAMPLE_CONFIG, temp)
        temp_path = temp.name

    yield temp_path

    # Clean up
    os.unlink(temp_path)

@pytest.fixture
def temp_data_file():
    """Create a temporary data file"""
    data = create_sample_data()

    with tempfile.NamedTemporaryFile(suffix='.csv', mode='w+', delete=False, encoding='utf-8') as temp:
        data.to_csv(temp.name, index=False)
        temp_path = temp.name

    yield temp_path

    # Clean up
    os.unlink(temp_path)

@pytest.fixture
def temp_results_dir():
    """Create a temporary results directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

def test_end_to_end_workflow(temp_config_file, temp_data_file, temp_results_dir):
    """Test the end-to-end workflow from configuration to results"""
    # 1. Load and validate configuration
    config = load_config(temp_config_file)
    assert validate_config(config) is True

    # Override results directory
    config['data']['results_folder'] = temp_results_dir

    # 2. Load data
    data = load_data(temp_data_file)

    # Add required attributes for save_results
    data.attrs = {
        'start_date': data.index.min().strftime('%Y-%m-%d %H:%M:%S'),
        'end_date': data.index.max().strftime('%Y-%m-%d %H:%M:%S'),
        'total_days': len(pd.Series(data.index.date).unique()),
        'total_candles': len(data)
    }

    # 3. Run strategy for each EMA pair
    all_results = []
    all_trades = []

    for ema_short, ema_long in config['strategy']['ema_pairs']:
        # Initialize strategy
        strategy = EMAHeikinAshiStrategy(ema_short, ema_long, config)

        # Run backtest
        results, trades = strategy.backtest(data, initial_capital=config['backtest']['initial_capital'])

        all_results.append(results)
        all_trades.append(trades)

    # 4. Check that results were generated
    assert len(all_results) == len(config['strategy']['ema_pairs'])
    assert len(all_trades) == len(config['strategy']['ema_pairs'])

    # 5. Check that results contain expected fields
    for result in all_results:
        # Check that result data contains expected fields
        assert 'ema_short' in result
        assert 'ema_long' in result
        assert 'total_trades' in result

        # If there are trades, check more detailed metrics
        if result['total_trades'] > 0:
            assert 'win_rate' in result
            assert 'profit_factor' in result
            assert 'total_profit' in result
            assert 'return_pct' in result
            assert 'max_drawdown_pct' in result

def test_different_trading_modes_integration(temp_data_file):
    """Test integration with different trading modes"""
    data = load_data(temp_data_file)

    # Test all trading modes
    for mode in ['BUY', 'SELL', 'SWING']:
        # Create config with this mode
        config = SAMPLE_CONFIG.copy()
        config['strategy'] = SAMPLE_CONFIG['strategy'].copy()
        config['strategy']['trading'] = {'mode': [mode]}

        # Run strategy
        strategy = EMAHeikinAshiStrategy(5, 10, config)
        results, trades = strategy.backtest(data, initial_capital=10000)

        # Check results
        assert isinstance(results, dict)
        assert isinstance(trades, list)
        assert 'total_trades' in results

        # If there are trades, check more detailed metrics
        if results['total_trades'] > 0:
            assert 'win_rate' in results
            assert 'profit_factor' in results

        # Check mode-specific behavior
        if trades:
            if mode == 'BUY':
                assert all(trade['position_type'] == 'LONG' for trade in trades)
            elif mode == 'SELL':
                assert all(trade['position_type'] == 'SHORT' for trade in trades)
            elif mode == 'SWING':
                # Should have both LONG and SHORT positions
                position_types = set(trade['position_type'] for trade in trades)
                # If there are trades, there should be at least one position type
                assert len(position_types) >= 1
