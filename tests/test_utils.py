"""
Tests for the utility functions.
"""

import pytest
import os
import tempfile
import pandas as pd
import yaml
from pathlib import Path
from datetime import datetime

from backtest.utils import load_config, load_data, save_results, calculate_performance_metrics

def test_load_config():
    """Test loading configuration from a YAML file"""
    # Create a temporary config file
    config = {
        "strategy": {
            "ema_pairs": [[9, 21], [13, 34]],
            "trading": {"mode": ["SWING"]}
        },
        "backtest": {"initial_capital": 100000},
        "data": {
            "data_folder": "data/market_data",
            "results_folder": "data/results",
            "timeframe": "1min"
        },
        "logging": {"level": "INFO"}
    }

    with tempfile.NamedTemporaryFile(suffix='.yaml', mode='w', delete=False, encoding='utf-8') as temp:
        yaml.dump(config, temp, default_flow_style=False)
        temp_path = temp.name

    try:
        # Test loading the config
        loaded_config = load_config(temp_path)

        # Check that the loaded config matches the original
        assert loaded_config["strategy"]["ema_pairs"] == config["strategy"]["ema_pairs"]
        assert loaded_config["backtest"]["initial_capital"] == config["backtest"]["initial_capital"]
        assert loaded_config["data"]["timeframe"] == config["data"]["timeframe"]

        # Check that directories were created
        assert os.path.exists(config["data"]["data_folder"])
        assert os.path.exists(config["data"]["results_folder"])

        # Test loading a non-existent file
        with pytest.raises(FileNotFoundError):
            load_config("non_existent_file.yaml")
    finally:
        # Clean up temporary file only
        os.unlink(temp_path)
        # Don't remove data directories as they may contain actual data

def test_load_data():
    """Test loading market data from a CSV file"""
    # Create a temporary CSV file with market data
    data = pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=5),
        'open': [100, 101, 102, 103, 104],
        'high': [105, 106, 107, 108, 109],
        'low': [95, 96, 97, 98, 99],
        'close': [102, 103, 104, 105, 106],
        'volume': [1000, 1100, 1200, 1300, 1400]
    })

    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as temp:
        data.to_csv(temp.name, index=False)
        temp_path = temp.name

    try:
        # Test loading the data
        loaded_data = load_data(temp_path)

        # Check that the loaded data matches the original
        assert len(loaded_data) == len(data)
        assert 'date' not in loaded_data.columns  # date should be the index
        assert loaded_data.index.name == 'date'
        assert loaded_data['close'].iloc[0] == 102

        # Check that attributes were set
        assert 'start_date' in loaded_data.attrs
        assert 'end_date' in loaded_data.attrs
        assert 'total_days' in loaded_data.attrs
        assert 'total_candles' in loaded_data.attrs

        # Test loading a non-existent file
        with pytest.raises(FileNotFoundError):
            load_data("non_existent_file.csv")
    finally:
        # Clean up
        os.unlink(temp_path)

def test_calculate_performance_metrics():
    """Test calculating performance metrics from trades"""
    # Create sample trades
    trades = [
        {'entry_time': '2023-01-01 10:00:00', 'exit_time': '2023-01-01 11:00:00', 'pnl': 1000, 'duration': 60},
        {'entry_time': '2023-01-02 10:00:00', 'exit_time': '2023-01-02 11:00:00', 'pnl': -500, 'duration': 60},
        {'entry_time': '2023-01-03 10:00:00', 'exit_time': '2023-01-03 11:00:00', 'pnl': 2000, 'duration': 60},
        {'entry_time': '2023-01-04 10:00:00', 'exit_time': '2023-01-04 11:00:00', 'pnl': -300, 'duration': 60}
    ]

    initial_capital = 10000

    # Calculate metrics
    metrics = calculate_performance_metrics(trades, initial_capital)

    # Check metrics
    assert metrics['total_trades'] == 4
    assert metrics['winning_trades'] == 2
    assert metrics['win_rate'] == 0.5
    assert metrics['total_profit'] == 2200
    assert metrics['profit_factor'] == 3.75  # 3000 / 800 (gross profit / gross loss)
    assert metrics['return_pct'] == 22.0
    assert metrics['avg_trade_duration'] == 60

    # Test with empty trades list
    empty_metrics = calculate_performance_metrics([], initial_capital)
    assert empty_metrics['total_trades'] == 0
    assert empty_metrics['win_rate'] == 0
