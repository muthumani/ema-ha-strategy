"""
Tests for the backtest.validate module.
"""

import pytest
import os
from pathlib import Path
import tempfile
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backtest.validate import run_single_test, validate_results
from unittest.mock import patch

class TestValidate:
    """Test cases for validation functions."""

    @pytest.fixture
    def sample_config(self):
        """Create a sample configuration for testing."""
        from tests.fixtures import create_sample_config
        config = create_sample_config()
        # Limit to 2 EMA pairs for faster tests
        config['strategy']['ema_pairs'] = [[9, 21], [13, 34]]
        return config

    @pytest.fixture
    def sample_data(self):
        """Create sample market data for testing."""
        from tests.fixtures import create_sample_data
        return create_sample_data()

    @patch('backtest.validate.EMAHeikinAshiStrategy')
    def test_run_single_test(self, mock_strategy, sample_config, sample_data):
        """Test running a single test."""
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
                'sharpe_ratio': 1.2
            },
            []  # trades
        )
        mock_strategy.return_value = mock_strategy_instance

        # Run a single test
        result = run_single_test(
            ema_short=13,
            ema_long=34,
            trading_mode='BUY',
            pattern='None',
            config=sample_config,
            data=sample_data,
            seed=42
        )

        # Verify the result
        assert result['ema_short'] == 13
        assert result['ema_long'] == 34
        assert result['total_trades'] == 50
        assert result['win_rate'] == 0.6
        assert result['profit_factor'] == 1.5
        assert result['total_profit'] == 10000
        assert result['return_pct'] == 40.0
        assert result['max_drawdown_pct'] == 15.0
        assert result['sharpe_ratio'] == 1.2
        assert result['trading_mode'] == 'BUY'
        assert result['pattern_length'] == 'None'

        # Verify that the strategy was initialized
        mock_strategy.assert_called_once()

        # Verify that backtest was called
        mock_strategy_instance.backtest.assert_called_once()

    @patch('backtest.validate.load_config')
    @patch('backtest.validate.load_data')
    @patch('backtest.validate.run_single_test')
    @patch('backtest.deterministic.DeterministicBacktest.run_backtest')
    def test_validate_results(self, mock_run_backtest, mock_run_single_test,
                            mock_load_data, mock_load_config, sample_config, sample_data):
        """Test validating results."""
        # Set up mock load_config
        mock_load_config.return_value = sample_config

        # Set up mock load_data
        mock_load_data.return_value = sample_data

        # Set up mock run_single_test
        mock_run_single_test.return_value = {
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
            with patch('backtest.validate.Path', return_value=output_dir):
                # Validate results
                validate_results(
                    config_path='config/test_config.yaml',
                    data_path='data/test_data.csv',
                    seed=42
                )

                # Verify that load_config was called
                mock_load_config.assert_called_once_with('config/test_config.yaml')

                # Verify that load_data was called
                mock_load_data.assert_called_once_with('data/test_data.csv')

                # Verify that run_single_test was called
                mock_run_single_test.assert_called_once()

                # Verify that run_backtest was called
                mock_run_backtest.assert_called_once()
