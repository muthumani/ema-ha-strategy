"""
Tests for the main module.
"""

import pytest
import os
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import parse_arguments, run_strategy, run_all_combinations_analysis, run_comparative_patterns_analysis, run_comparative_analysis

class TestMain:
    """Test cases for main module."""

    @pytest.fixture
    def sample_config(self):
        """Create a sample configuration for testing."""
        from tests.fixtures import create_sample_config
        config = create_sample_config()
        # Add logging configuration
        config['logging'] = {'level': 'INFO'}
        # Limit to 2 EMA pairs for faster tests
        config['strategy']['ema_pairs'] = [[9, 21], [13, 34]]
        return config

    @pytest.fixture
    def sample_data(self):
        """Create sample market data for testing."""
        from tests.fixtures import create_sample_data
        data = create_sample_data()
        # Add attributes for testing
        data.attrs = {
            'start_date': '2023-01-01 09:15:00',
            'end_date': '2023-01-31 15:30:00',
            'total_days': 21,
            'total_candles': 100
        }
        return data

    @patch('argparse.ArgumentParser.parse_args')
    def test_parse_arguments(self, mock_parse_args):
        """Test parsing command line arguments."""
        # Set up mock parse_args
        mock_args = MagicMock()
        mock_args.config = 'config/test_config.yaml'
        mock_args.no_config = False
        mock_args.data = 'data/test_data.csv'
        mock_args.symbol = 'NIFTY'
        mock_args.output = 'data/test_results'
        mock_args.debug = True
        mock_args.mode = 'BUY'
        mock_args.candle_pattern = '2'
        mock_args.compare = False
        mock_args.compare_patterns = False
        mock_args.all_combinations = False
        mock_args.report = False
        mock_args.execution_mode = 'standard'
        mock_args.seed = 42
        mock_parse_args.return_value = mock_args

        # Parse arguments
        args = parse_arguments()

        # Verify the arguments
        assert args.config == 'config/test_config.yaml'
        assert args.no_config is False
        assert args.data == 'data/test_data.csv'
        assert args.symbol == 'NIFTY'
        assert args.output == 'data/test_results'
        assert args.debug is True
        assert args.mode == 'BUY'
        assert args.candle_pattern == '2'
        assert args.compare is False
        assert args.compare_patterns is False
        assert args.all_combinations is False
        assert args.report is False
        assert args.execution_mode == 'standard'
        assert args.seed == 42

    @patch('main.get_config')
    @patch('main.validate_config')
    @patch('main.load_data')
    @patch('main.EMAHeikinAshiStrategy')
    @patch('main.save_results')
    def test_run_strategy(self, mock_save_results, mock_strategy, mock_load_data,
                        mock_validate_config, mock_get_config, sample_config, sample_data):
        """Test running the strategy."""
        # Set up mock get_config
        mock_get_config.return_value = sample_config

        # Set up mock validate_config
        mock_validate_config.return_value = True

        # Set up mock load_data
        mock_load_data.return_value = sample_data

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

        # Run the strategy
        results, trades = run_strategy(
            config_path='config/test_config.yaml',
            data_path='data/test_data.csv',
            symbol='NIFTY',
            output_dir='data/test_results',
            mode='BUY',
            candle_pattern=2
        )

        # Verify the results
        assert len(results) == 2  # 2 EMA pairs

        # Verify that get_config was called
        mock_get_config.assert_called_once_with('config/test_config.yaml')

        # Verify that validate_config was called
        mock_validate_config.assert_called_once_with(sample_config)

        # Verify that load_data was called
        mock_load_data.assert_called_once()

        # Verify that the strategy was initialized for each EMA pair
        assert mock_strategy.call_count == 2

        # Verify that backtest was called for each EMA pair
        assert mock_strategy_instance.backtest.call_count == 2

        # Verify that save_results was called for each EMA pair
        assert mock_save_results.call_count == 2

    @patch('main.get_trading_modes')
    @patch('main.get_candle_patterns')
    @patch('main.get_config')
    @patch('main.load_data')
    @patch('main.run_parallel_backtests')
    def test_run_all_combinations_analysis(self, mock_run_parallel, mock_load_data,
                                         mock_get_config, mock_get_candle_patterns,
                                         mock_get_trading_modes, sample_config, sample_data):
        """Test running all combinations analysis."""
        # Set up mock get_trading_modes
        mock_get_trading_modes.return_value = ['BUY', 'SELL', 'SWING']

        # Set up mock get_candle_patterns
        mock_get_candle_patterns.return_value = [2, 3, None]

        # Set up mock get_config
        mock_get_config.return_value = sample_config

        # Set up mock load_data
        mock_load_data.return_value = sample_data

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

        # Run all combinations analysis
        results, trades = run_all_combinations_analysis(
            config_path='config/test_config.yaml',
            data_path='data/test_data.csv',
            symbol='NIFTY',
            deterministic=True,
            sequential=False,
            seed=42,
            cross_validate=False
        )

        # Verify the results
        assert len(results) == 2

        # Verify that get_trading_modes was called
        mock_get_trading_modes.assert_called_once()

        # Verify that get_candle_patterns was called
        mock_get_candle_patterns.assert_called_once()

        # Verify that get_config was called
        mock_get_config.assert_called_once_with('config/test_config.yaml')

        # Verify that load_data was called
        mock_load_data.assert_called_once()

        # Verify that run_parallel_backtests was called
        mock_run_parallel.assert_called_once()

    @patch('main.run_strategy')
    def test_run_comparative_patterns_analysis(self, mock_run_strategy, sample_config, sample_data):
        """Test running comparative patterns analysis."""
        # Set up mock run_strategy
        mock_run_strategy.side_effect = [
            (  # Results for pattern 2
                [
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
                    {
                        'ema_short': 13,
                        'ema_long': 34,
                        'total_trades': 40,
                        'win_rate': 0.7,
                        'profit_factor': 2.0,
                        'total_profit': 15000,
                        'return_pct': 60.0,
                        'max_drawdown_pct': 10.0,
                        'sharpe_ratio': 1.5
                    }
                ],
                []  # trades
            ),
            (  # Results for pattern 3
                [
                    {
                        'ema_short': 9,
                        'ema_long': 21,
                        'total_trades': 45,
                        'win_rate': 0.65,
                        'profit_factor': 1.6,
                        'total_profit': 11000,
                        'return_pct': 44.0,
                        'max_drawdown_pct': 14.0,
                        'sharpe_ratio': 1.3
                    },
                    {
                        'ema_short': 13,
                        'ema_long': 34,
                        'total_trades': 35,
                        'win_rate': 0.75,
                        'profit_factor': 2.2,
                        'total_profit': 16000,
                        'return_pct': 64.0,
                        'max_drawdown_pct': 9.0,
                        'sharpe_ratio': 1.6
                    }
                ],
                []  # trades
            )
        ]

        # Run comparative patterns analysis
        results, trades = run_comparative_patterns_analysis(
            config_path='config/test_config.yaml',
            data_path='data/test_data.csv',
            symbol='NIFTY',
            output_dir='data/test_results',
            mode='BUY'
        )

        # Verify the results
        assert len(results) == 2  # 2 patterns
        assert 2 in results
        assert 3 in results
        assert len(results[2]) == 2  # 2 EMA pairs
        assert len(results[3]) == 2  # 2 EMA pairs

        # Verify that run_strategy was called for each pattern
        assert mock_run_strategy.call_count == 2

        # Verify the call arguments
        mock_run_strategy.assert_any_call(
            config_path='config/test_config.yaml',
            data_path='data/test_data.csv',
            symbol='NIFTY',
            output_dir='data/test_results',
            mode='BUY',
            candle_pattern=2
        )
        mock_run_strategy.assert_any_call(
            config_path='config/test_config.yaml',
            data_path='data/test_data.csv',
            symbol='NIFTY',
            output_dir='data/test_results',
            mode='BUY',
            candle_pattern=3
        )

    @patch('main.run_strategy')
    def test_run_comparative_analysis(self, mock_run_strategy, sample_config, sample_data):
        """Test running comparative analysis."""
        # Set up mock run_strategy
        mock_run_strategy.side_effect = [
            (  # Results for BUY mode
                [
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
                    {
                        'ema_short': 13,
                        'ema_long': 34,
                        'total_trades': 40,
                        'win_rate': 0.7,
                        'profit_factor': 2.0,
                        'total_profit': 15000,
                        'return_pct': 60.0,
                        'max_drawdown_pct': 10.0,
                        'sharpe_ratio': 1.5
                    }
                ],
                []  # trades
            ),
            (  # Results for SELL mode
                [
                    {
                        'ema_short': 9,
                        'ema_long': 21,
                        'total_trades': 45,
                        'win_rate': 0.65,
                        'profit_factor': 1.6,
                        'total_profit': 11000,
                        'return_pct': 44.0,
                        'max_drawdown_pct': 14.0,
                        'sharpe_ratio': 1.3
                    },
                    {
                        'ema_short': 13,
                        'ema_long': 34,
                        'total_trades': 35,
                        'win_rate': 0.75,
                        'profit_factor': 2.2,
                        'total_profit': 16000,
                        'return_pct': 64.0,
                        'max_drawdown_pct': 9.0,
                        'sharpe_ratio': 1.6
                    }
                ],
                []  # trades
            ),
            (  # Results for SWING mode
                [
                    {
                        'ema_short': 9,
                        'ema_long': 21,
                        'total_trades': 55,
                        'win_rate': 0.55,
                        'profit_factor': 1.4,
                        'total_profit': 9000,
                        'return_pct': 36.0,
                        'max_drawdown_pct': 16.0,
                        'sharpe_ratio': 1.1
                    },
                    {
                        'ema_short': 13,
                        'ema_long': 34,
                        'total_trades': 45,
                        'win_rate': 0.65,
                        'profit_factor': 1.8,
                        'total_profit': 14000,
                        'return_pct': 56.0,
                        'max_drawdown_pct': 11.0,
                        'sharpe_ratio': 1.4
                    }
                ],
                []  # trades
            )
        ]

        # Run comparative analysis
        results, trades = run_comparative_analysis(
            config_path='config/test_config.yaml',
            data_path='data/test_data.csv',
            symbol='NIFTY',
            output_dir='data/test_results'
        )

        # Verify the results
        assert len(results) == 3  # 3 modes
        assert 'BUY' in results
        assert 'SELL' in results
        assert 'SWING' in results
        assert len(results['BUY']) == 2  # 2 EMA pairs
        assert len(results['SELL']) == 2  # 2 EMA pairs
        assert len(results['SWING']) == 2  # 2 EMA pairs

        # Verify that run_strategy was called for each mode
        assert mock_run_strategy.call_count == 3

        # Verify the call arguments
        mock_run_strategy.assert_any_call(
            config_path='config/test_config.yaml',
            data_path='data/test_data.csv',
            symbol='NIFTY',
            output_dir='data/test_results',
            mode='BUY',
            candle_pattern=None
        )
        mock_run_strategy.assert_any_call(
            config_path='config/test_config.yaml',
            data_path='data/test_data.csv',
            symbol='NIFTY',
            output_dir='data/test_results',
            mode='SELL',
            candle_pattern=None
        )
        mock_run_strategy.assert_any_call(
            config_path='config/test_config.yaml',
            data_path='data/test_data.csv',
            symbol='NIFTY',
            output_dir='data/test_results',
            mode='SWING',
            candle_pattern=None
        )
