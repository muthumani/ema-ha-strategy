"""
Tests for the backtest.cross_validate module.
"""

import pytest
import os
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backtest.cross_validate import run_sequential_backtest, run_parallel_validation
from unittest.mock import patch

class TestCrossValidate:
    """Test cases for cross validation functions."""

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

    @patch('backtest.cross_validate.EMAHeikinAshiStrategy')
    def test_run_sequential_backtest(self, mock_strategy, sample_config, sample_data):
        """Test running sequential backtests."""
        # Set up mock strategy
        mock_strategy_instance = MagicMock()
        mock_strategy_instance.backtest.return_value = (
            {
                'ema_short': 9,
                'ema_long': 21,
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

        # Define trading modes and candle patterns
        trading_modes = ['BUY']
        candle_patterns = ['2']

        # Run sequential backtests
        results = run_sequential_backtest(
            config=sample_config,
            data=sample_data,
            trading_modes=trading_modes,
            candle_patterns=candle_patterns,
            seed=42
        )

        # Verify the results
        assert len(results) == 2  # 2 EMA pairs

        # Verify that the strategy was initialized for each combination
        assert mock_strategy.call_count == 2

        # Verify that backtest was called for each combination
        assert mock_strategy_instance.backtest.call_count == 2

        # Verify the result structure
        for result in results:
            assert 'ema_short' in result
            assert 'ema_long' in result
            assert 'total_trades' in result
            assert 'win_rate' in result
            assert 'profit_factor' in result
            assert 'total_profit' in result
            assert 'return_pct' in result
            assert 'max_drawdown_pct' in result
            assert 'sharpe_ratio' in result
            assert 'trading_mode' in result
            assert 'pattern_length' in result

    @patch('backtest.cross_validate.EMAHeikinAshiStrategy')
    def test_run_sequential_backtest_with_none_pattern(self, mock_strategy, sample_config, sample_data):
        """Test running sequential backtests with 'None' pattern."""
        # Set up mock strategy
        mock_strategy_instance = MagicMock()
        mock_strategy_instance.backtest.return_value = (
            {
                'ema_short': 9,
                'ema_long': 21,
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

        # Define trading modes and candle patterns
        trading_modes = ['BUY']
        candle_patterns = ['None']

        # Run sequential backtests
        results = run_sequential_backtest(
            config=sample_config,
            data=sample_data,
            trading_modes=trading_modes,
            candle_patterns=candle_patterns,
            seed=42
        )

        # Verify the results
        assert len(results) == 2  # 2 EMA pairs

        # Verify that the strategy was initialized for each combination
        assert mock_strategy.call_count == 2

        # Verify that backtest was called for each combination
        assert mock_strategy_instance.backtest.call_count == 2

        # Verify the result structure
        for result in results:
            assert result['pattern_length'] == 'None'

    @patch('backtest.cross_validate.EMAHeikinAshiStrategy')
    def test_run_sequential_backtest_multiple_modes_patterns(self, mock_strategy, sample_config, sample_data):
        """Test running sequential backtests with multiple modes and patterns."""
        # Set up mock strategy
        mock_strategy_instance = MagicMock()
        mock_strategy_instance.backtest.return_value = (
            {
                'ema_short': 9,
                'ema_long': 21,
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

        # Define trading modes and candle patterns
        trading_modes = ['BUY', 'SELL', 'SWING']
        candle_patterns = ['None', '2', '3']

        # Run sequential backtests
        results = run_sequential_backtest(
            config=sample_config,
            data=sample_data,
            trading_modes=trading_modes,
            candle_patterns=candle_patterns,
            seed=42
        )

        # Verify the results
        assert len(results) == 18  # 2 EMA pairs * 3 modes * 3 patterns

        # Verify that the strategy was initialized for each combination
        assert mock_strategy.call_count == 18

        # Verify that backtest was called for each combination
        assert mock_strategy_instance.backtest.call_count == 18

    @patch('backtest.cross_validate.EMAHeikinAshiStrategy')
    def test_run_sequential_backtest_missing_strategy_config(self, mock_strategy, sample_data):
        """Test running sequential backtests with missing strategy configuration."""
        # Set up mock strategy
        mock_strategy_instance = MagicMock()
        mock_strategy_instance.backtest.return_value = (
            {
                'ema_short': 9,
                'ema_long': 21,
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

        # Create a config without strategy section
        config_without_strategy = {
            'backtest': {
                'initial_capital': 25000
            },
            'data': {
                'data_folder': 'data/market_data',
                'results_folder': 'data/results',
                'timeframe': '1min'
            }
        }

        # Add the ema_pairs to the config to avoid KeyError
        config_without_strategy['strategy'] = {'ema_pairs': [[9, 21], [13, 34]]}

        # Define trading modes and candle patterns
        trading_modes = ['BUY']
        candle_patterns = ['2']

        # Run sequential backtests
        results = run_sequential_backtest(
            config=config_without_strategy,
            data=sample_data,
            trading_modes=trading_modes,
            candle_patterns=candle_patterns,
            seed=42
        )

        # Verify the results
        assert len(results) == 2  # 2 EMA pairs

        # Verify that the strategy config was created
        assert 'trading' in config_without_strategy['strategy']
        assert 'ha_patterns' in config_without_strategy['strategy']

    @patch('backtest.cross_validate.load_config')
    @patch('backtest.cross_validate.load_data')
    @patch('backtest.cross_validate.run_sequential_backtest')
    @patch('backtest.cross_validate.run_parallel_backtests')
    def test_run_parallel_validation_identical_results(self, mock_run_parallel, mock_run_sequential,
                                   mock_load_data, mock_load_config, sample_config, sample_data):
        """Test running parallel validation with identical results."""
        # Set up mock load_config
        mock_load_config.return_value = sample_config

        # Set up mock load_data
        mock_load_data.return_value = sample_data

        # Set up mock run_sequential_backtest
        mock_run_sequential.return_value = [
            {
                'ema_short': 9,
                'ema_long': 21,
                'total_trades': 50,
                'win_rate': 0.6,
                'profit_factor': 1.5,
                'total_profit': 10000,
                'return_pct': 40.0,
                'max_drawdown_pct': 15.0,
                'sharpe_ratio': 1.2,
                'trading_mode': 'BUY',
                'pattern_length': '2'
            },
            {
                'ema_short': 13,
                'ema_long': 34,
                'total_trades': 40,
                'win_rate': 0.7,
                'profit_factor': 2.0,
                'total_profit': 15000,
                'return_pct': 60.0,
                'max_drawdown_pct': 10.0,
                'sharpe_ratio': 1.5,
                'trading_mode': 'BUY',
                'pattern_length': '2'
            }
        ]

        # Set up mock run_parallel_backtests with identical results
        mock_run_parallel.return_value = [
            {
                'ema_short': 9,
                'ema_long': 21,
                'total_trades': 50,
                'win_rate': 0.6,
                'profit_factor': 1.5,
                'total_profit': 10000,
                'return_pct': 40.0,
                'max_drawdown_pct': 15.0,
                'sharpe_ratio': 1.2,
                'trading_mode': 'BUY',
                'pattern_length': '2'
            },
            {
                'ema_short': 13,
                'ema_long': 34,
                'total_trades': 40,
                'win_rate': 0.7,
                'profit_factor': 2.0,
                'total_profit': 15000,
                'return_pct': 60.0,
                'max_drawdown_pct': 10.0,
                'sharpe_ratio': 1.5,
                'trading_mode': 'BUY',
                'pattern_length': '2'
            }
        ]

        # Create a temporary directory for validation results
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up the output directory
            output_dir = Path(temp_dir) / 'data/validation'
            output_dir.mkdir(parents=True, exist_ok=True)

            # Patch the output directory and open function
            with patch('backtest.cross_validate.Path', return_value=output_dir), \
                 patch('builtins.open', new_callable=unittest.mock.mock_open), \
                 patch('json.dump'):
                # Run parallel validation
                run_parallel_validation(
                    config_path='config/test_config.yaml',
                    data_path='data/test_data.csv',
                    seed=42
                )

                # Verify that load_config was called
                mock_load_config.assert_called_once_with('config/test_config.yaml')

                # Verify that load_data was called
                mock_load_data.assert_called_once_with('data/test_data.csv')

                # Verify that run_sequential_backtest was called
                mock_run_sequential.assert_called_once()

                # Verify that run_parallel_backtests was called
                mock_run_parallel.assert_called_once()

    @patch('backtest.cross_validate.load_config')
    @patch('backtest.cross_validate.load_data')
    @patch('backtest.cross_validate.run_sequential_backtest')
    @patch('backtest.cross_validate.run_parallel_backtests')
    def test_run_parallel_validation_different_results(self, mock_run_parallel, mock_run_sequential,
                                   mock_load_data, mock_load_config, sample_config, sample_data):
        """Test running parallel validation with different results."""
        # Set up mock load_config
        mock_load_config.return_value = sample_config

        # Set up mock load_data
        mock_load_data.return_value = sample_data

        # Set up mock run_sequential_backtest
        mock_run_sequential.return_value = [
            {
                'ema_short': 9,
                'ema_long': 21,
                'total_trades': 50,
                'win_rate': 0.6,
                'profit_factor': 1.5,
                'total_profit': 10000,
                'return_pct': 40.0,
                'max_drawdown_pct': 15.0,
                'sharpe_ratio': 1.2,
                'trading_mode': 'BUY',
                'pattern_length': '2'
            },
            {
                'ema_short': 13,
                'ema_long': 34,
                'total_trades': 40,
                'win_rate': 0.7,
                'profit_factor': 2.0,
                'total_profit': 15000,
                'return_pct': 60.0,
                'max_drawdown_pct': 10.0,
                'sharpe_ratio': 1.5,
                'trading_mode': 'BUY',
                'pattern_length': '2'
            }
        ]

        # Set up mock run_parallel_backtests with different results
        mock_run_parallel.return_value = [
            {
                'ema_short': 9,
                'ema_long': 21,
                'total_trades': 51,  # Different value
                'win_rate': 0.61,    # Different value
                'profit_factor': 1.51, # Different value
                'total_profit': 10100, # Different value
                'return_pct': 40.1,   # Different value
                'max_drawdown_pct': 15.1, # Different value
                'sharpe_ratio': 1.21,  # Different value
                'trading_mode': 'BUY',
                'pattern_length': '2'
            },
            {
                'ema_short': 13,
                'ema_long': 34,
                'total_trades': 40,
                'win_rate': 0.7,
                'profit_factor': 2.0,
                'total_profit': 15000,
                'return_pct': 60.0,
                'max_drawdown_pct': 10.0,
                'sharpe_ratio': 1.5,
                'trading_mode': 'BUY',
                'pattern_length': '2'
            }
        ]

        # Create a temporary directory for validation results
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up the output directory
            output_dir = Path(temp_dir) / 'data/validation'
            output_dir.mkdir(parents=True, exist_ok=True)

            # Patch the output directory and open function
            with patch('backtest.cross_validate.Path', return_value=output_dir), \
                 patch('builtins.open', new_callable=unittest.mock.mock_open), \
                 patch('json.dump'):
                # Run parallel validation
                run_parallel_validation(
                    config_path='config/test_config.yaml',
                    data_path='data/test_data.csv',
                    seed=42
                )

                # Verify that load_config was called
                mock_load_config.assert_called_once_with('config/test_config.yaml')

                # Verify that load_data was called
                mock_load_data.assert_called_once_with('data/test_data.csv')

                # Verify that run_sequential_backtest was called
                mock_run_sequential.assert_called_once()

                # Verify that run_parallel_backtests was called
                mock_run_parallel.assert_called_once()

    @patch('backtest.cross_validate.load_config')
    @patch('backtest.cross_validate.load_data')
    @patch('backtest.cross_validate.run_sequential_backtest')
    @patch('backtest.cross_validate.run_parallel_backtests')
    def test_run_parallel_validation_different_length(self, mock_run_parallel, mock_run_sequential,
                                   mock_load_data, mock_load_config, sample_config, sample_data):
        """Test running parallel validation with different number of results."""
        # Set up mock load_config
        mock_load_config.return_value = sample_config

        # Set up mock load_data
        mock_load_data.return_value = sample_data

        # Set up mock run_sequential_backtest
        mock_run_sequential.return_value = [
            {
                'ema_short': 9,
                'ema_long': 21,
                'total_trades': 50,
                'win_rate': 0.6,
                'profit_factor': 1.5,
                'total_profit': 10000,
                'return_pct': 40.0,
                'max_drawdown_pct': 15.0,
                'sharpe_ratio': 1.2,
                'trading_mode': 'BUY',
                'pattern_length': '2'
            },
            {
                'ema_short': 13,
                'ema_long': 34,
                'total_trades': 40,
                'win_rate': 0.7,
                'profit_factor': 2.0,
                'total_profit': 15000,
                'return_pct': 60.0,
                'max_drawdown_pct': 10.0,
                'sharpe_ratio': 1.5,
                'trading_mode': 'BUY',
                'pattern_length': '2'
            }
        ]

        # Set up mock run_parallel_backtests with fewer results
        mock_run_parallel.return_value = [
            {
                'ema_short': 9,
                'ema_long': 21,
                'total_trades': 50,
                'win_rate': 0.6,
                'profit_factor': 1.5,
                'total_profit': 10000,
                'return_pct': 40.0,
                'max_drawdown_pct': 15.0,
                'sharpe_ratio': 1.2,
                'trading_mode': 'BUY',
                'pattern_length': '2'
            }
        ]

        # Create a temporary directory for validation results
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up the output directory
            output_dir = Path(temp_dir) / 'data/validation'
            output_dir.mkdir(parents=True, exist_ok=True)

            # Patch the output directory and open function
            with patch('backtest.cross_validate.Path', return_value=output_dir), \
                 patch('builtins.open', new_callable=unittest.mock.mock_open), \
                 patch('json.dump'):
                # Run parallel validation
                run_parallel_validation(
                    config_path='config/test_config.yaml',
                    data_path='data/test_data.csv',
                    seed=42
                )

                # Verify that load_config was called
                mock_load_config.assert_called_once_with('config/test_config.yaml')

                # Verify that load_data was called
                mock_load_data.assert_called_once_with('data/test_data.csv')

                # Verify that run_sequential_backtest was called
                mock_run_sequential.assert_called_once()

                # Verify that run_parallel_backtests was called
                mock_run_parallel.assert_called_once()

    @patch('backtest.cross_validate.load_config')
    @patch('backtest.cross_validate.load_data')
    @patch('backtest.cross_validate.run_sequential_backtest')
    @patch('backtest.cross_validate.run_parallel_backtests')
    def test_run_parallel_validation_no_data_path(self, mock_run_parallel, mock_run_sequential,
                                   mock_load_data, mock_load_config, sample_config, sample_data):
        """Test running parallel validation without specifying data_path."""
        # Set up mock load_config
        mock_load_config.return_value = sample_config

        # Set up mock load_data
        mock_load_data.return_value = sample_data

        # Set up mock run_sequential_backtest
        mock_run_sequential.return_value = [
            {
                'ema_short': 9,
                'ema_long': 21,
                'total_trades': 50,
                'win_rate': 0.6,
                'profit_factor': 1.5,
                'total_profit': 10000,
                'return_pct': 40.0,
                'max_drawdown_pct': 15.0,
                'sharpe_ratio': 1.2,
                'trading_mode': 'BUY',
                'pattern_length': '2'
            }
        ]

        # Set up mock run_parallel_backtests
        mock_run_parallel.return_value = [
            {
                'ema_short': 9,
                'ema_long': 21,
                'total_trades': 50,
                'win_rate': 0.6,
                'profit_factor': 1.5,
                'total_profit': 10000,
                'return_pct': 40.0,
                'max_drawdown_pct': 15.0,
                'sharpe_ratio': 1.2,
                'trading_mode': 'BUY',
                'pattern_length': '2'
            }
        ]

        # Create a temporary directory for validation results
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set up the output directory
            output_dir = Path(temp_dir) / 'data/validation'
            output_dir.mkdir(parents=True, exist_ok=True)

            # Patch the output directory and open function
            with patch('backtest.cross_validate.Path', return_value=output_dir), \
                 patch('builtins.open', new_callable=unittest.mock.mock_open), \
                 patch('json.dump'):
                # Run parallel validation without data_path
                run_parallel_validation(
                    config_path='config/test_config.yaml',
                    data_path=None,
                    seed=42
                )

                # Verify that load_config was called
                mock_load_config.assert_called_once_with('config/test_config.yaml')

                # Verify that load_data was called with the path from config
                mock_load_data.assert_called_once()

    @patch('backtest.cross_validate.run_parallel_validation')
    @patch('backtest.cross_validate.argparse.ArgumentParser.parse_args')
    def test_main_function(self, mock_parse_args, mock_run_parallel_validation):
        """Test the main function."""
        # Set up mock parse_args
        mock_args = MagicMock()
        mock_args.config = 'config/test_config.yaml'
        mock_args.data = 'data/test_data.csv'
        mock_args.seed = 42
        mock_parse_args.return_value = mock_args

        # Import the main function
        from backtest.cross_validate import main

        # Call the main function
        main()

        # Verify that run_parallel_validation was called with the correct arguments
        mock_run_parallel_validation.assert_called_once_with(
            'config/test_config.yaml',
            'data/test_data.csv',
            42
        )
