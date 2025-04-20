"""
Tests for the backtest.utils module.
"""

import pytest
import pandas as pd
import numpy as np
import os
import json
from pathlib import Path
import tempfile
import yaml
import unittest
from datetime import datetime
from unittest.mock import patch, mock_open, MagicMock

# Add the project root directory to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backtest.utils import load_config, load_data, save_results

class TestBacktestUtils:
    """Test cases for backtest.utils module."""

    @patch('os.path.exists')
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data='''strategy:
  ema_pairs: [[9, 21], [13, 34], [21, 55]]
  trading:
    mode: [SWING]
  ha_patterns:
    enabled: true
    confirmation_candles: [2]
backtest:
  initial_capital: 25000
data:
  data_folder: data/market_data
  results_folder: data/results
  timeframe: 1min
''')
    def test_load_config(self, mock_open, mock_exists):
        """Test loading configuration from a file."""
        # Set up mocks
        mock_exists.return_value = True

        # Test loading the config
        config = load_config('config/test_config.yaml')

        # Verify the config was loaded correctly
        assert config['strategy']['ema_pairs'] == [[9, 21], [13, 34], [21, 55]]
        assert config['strategy']['trading']['mode'] == ['SWING']
        assert config['strategy']['ha_patterns']['enabled'] is True
        assert config['strategy']['ha_patterns']['confirmation_candles'] == [2]
        assert config['backtest']['initial_capital'] == 25000
        assert config['data']['data_folder'] == 'data/market_data'
        assert config['data']['results_folder'] == 'data/results'
        assert config['data']['timeframe'] == '1min'

    @patch('os.path.exists')
    @patch('pandas.read_csv')
    def test_load_data(self, mock_read_csv, mock_exists):
        """Test loading market data from a file."""
        # Create sample data
        dates = pd.date_range(start='2023-01-01', periods=100, freq='1min')
        mock_df = pd.DataFrame({
            'date': dates,
            'open': np.random.rand(100) * 100 + 100,
            'high': np.random.rand(100) * 100 + 150,
            'low': np.random.rand(100) * 100 + 50,
            'close': np.random.rand(100) * 100 + 100,
            'volume': np.random.randint(1000, 10000, 100)
        })

        # Set up mocks
        mock_exists.return_value = True
        mock_read_csv.return_value = mock_df

        # Test loading the data
        df = load_data('data/test_data.csv')

        # Verify the data was loaded correctly
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 100
        assert 'open' in df.columns
        assert 'high' in df.columns
        assert 'low' in df.columns
        assert 'close' in df.columns
        assert 'volume' in df.columns

        # Check that the data info was added as attributes
        assert hasattr(df, 'attrs')
        assert 'start_date' in df.attrs
        assert 'end_date' in df.attrs
        assert 'total_days' in df.attrs
        assert 'total_candles' in df.attrs

    @patch('backtest.utils.Path.mkdir')
    @patch('backtest.utils.open', new_callable=unittest.mock.mock_open)
    @patch('backtest.utils.json.dump')
    @patch('backtest.utils.pd.DataFrame')
    def test_save_results(self, mock_dataframe, mock_json_dump, mock_open, mock_mkdir):
        """Test saving backtest results to a file."""
        # Set up mocks
        mock_dataframe_instance = MagicMock()
        mock_dataframe.return_value = mock_dataframe_instance

        # Create sample results and trades
        results = {
            'ema_short': 9,
            'ema_long': 21,
            'total_trades': 50,
            'win_rate': 0.6,
            'profit_factor': 1.5,
            'total_profit': 10000,
            'return_pct': 40.0,
            'max_drawdown_pct': 15.0,
            'monthly_returns_avg': 3.0,
            'monthly_returns_std': 2.0
        }

        trades = [
            {
                'entry_date': '2023-01-01 09:30:00',
                'exit_date': '2023-01-01 15:15:00',
                'entry_price': 100.0,
                'exit_price': 110.0,
                'profit_pct': 10.0,
                'profit': 1000.0,
                'exit_reason': 'Signal'
            },
            {
                'entry_date': '2023-01-02 09:30:00',
                'exit_date': '2023-01-02 15:15:00',
                'entry_price': 110.0,
                'exit_price': 105.0,
                'profit_pct': -4.5,
                'profit': -500.0,
                'exit_reason': 'ForceExit'
            }
        ]

        data_attrs = {
            'start_date': '2023-01-01 09:15:00',
            'end_date': '2023-01-31 15:30:00',
            'total_days': 21,
            'total_candles': 8400
        }

        # Save the results
        with patch('backtest.utils.datetime') as mock_datetime:
            mock_datetime.now.return_value.strftime.return_value = '20230101_120000'
            result_files = save_results(results, trades, 'NIFTY', 9, 21, data_attrs)

        # Verify that the necessary functions were called
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_open.assert_called()
        mock_json_dump.assert_called_once()
        mock_dataframe_instance.to_csv.assert_called_once()


