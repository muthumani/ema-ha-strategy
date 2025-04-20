"""
Tests for the backtest.quick_validate module.
"""

import pytest
import os
import json
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backtest.quick_validate import run_quick_validation
from unittest.mock import patch

class TestQuickValidate:
    """Test cases for quick validation functions."""

    @pytest.fixture
    def sample_config(self):
        """Create a sample configuration for testing."""
        return {
            'strategy': {
                'ema_pairs': [[9, 21], [13, 34]],
                'trading': {
                    'mode': ['SWING']
                },
                'ha_patterns': {
                    'enabled': True,
                    'confirmation_candles': [2]
                }
            },
            'backtest': {
                'initial_capital': 25000
            },
            'data': {
                'data_folder': 'data/market_data',
                'results_folder': 'data/results',
                'timeframe': '1min'
            }
        }

    @pytest.fixture
    def sample_data(self):
        """Create sample market data for testing."""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='1min')
        data = pd.DataFrame({
            'date': dates,
            'open': np.random.rand(100) * 100 + 100,
            'high': np.random.rand(100) * 100 + 150,
            'low': np.random.rand(100) * 100 + 50,
            'close': np.random.rand(100) * 100 + 100,
            'volume': np.random.randint(1000, 10000, 100)
        })
        data.set_index('date', inplace=True)
        return data

    @patch('backtest.quick_validate.load_config')
    @patch('backtest.quick_validate.load_data')
    @patch('backtest.quick_validate.EMAHeikinAshiStrategy')
    @patch('backtest.quick_validate.DeterministicBacktest.run_backtest')
    def test_run_quick_validation(self, mock_run_backtest, mock_strategy,
                                mock_load_data, mock_load_config, sample_config, sample_data):
        """Test running quick validation."""
        # Set up mock load_config
        mock_load_config.return_value = sample_config

        # Set up mock load_data
        mock_load_data.return_value = sample_data

        # Set up mock strategy
        mock_strategy_instance = MagicMock()
        mock_strategy_instance.backtest.return_value = (
            {
                'ema_short': 13,
                'ema_long': 34,
                'total_trades': 50,
                'win_rate': 0.6,
                'profit_factor': 1.5,
                'total_profit': 10000,
                'return_pct': 40.0,
                'max_drawdown_pct': 15.0,
                'sharpe_ratio': 1.2,
                'trading_mode': 'BUY',
                'pattern_length': 'None'
            },
            []  # trades
        )
        mock_strategy.return_value = mock_strategy_instance

        # Set up mock run_backtest
        mock_run_backtest.return_value = {
            'ema_short': 13,
            'ema_long': 34,
            'total_trades': 50,
            'win_rate': 0.6,
            'profit_factor': 1.5,
            'total_profit': 10000,
            'return_pct': 40.0,
            'max_drawdown_pct': 15.0,
            'sharpe_ratio': 1.2,
            'trading_mode': 'BUY',
            'pattern_length': 'None'
        }

        # Create a temporary directory for validation results
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up the output directory
            output_dir = Path(temp_dir) / 'data/validation'
            output_dir.mkdir(parents=True, exist_ok=True)

            # Patch the output directory
            with patch('backtest.quick_validate.Path', return_value=output_dir):
                # Run quick validation
                run_quick_validation(
                    config_path='config/test_config.yaml',
                    data_path='data/test_data.csv',
                    seed=42
                )

                # Verify that load_config was called
                mock_load_config.assert_called_once_with('config/test_config.yaml')

                # Verify that load_data was called
                mock_load_data.assert_called_once_with('data/test_data.csv')

                # Verify that the strategy was initialized
                mock_strategy.assert_called_once()

                # Verify that backtest was called
                mock_strategy_instance.backtest.assert_called_once()

                # Verify that run_backtest was called
                mock_run_backtest.assert_called_once_with(
                    ema_short=13,
                    ema_long=34,
                    config=sample_config,
                    data=sample_data,
                    trading_mode='BUY',
                    pattern='None',
                    seed=42
                )
