"""
Tests for the backtest.deterministic module.
"""

import pytest
import os
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backtest.deterministic import DeterministicBacktest

class TestDeterministicBacktest:
    """Test cases for DeterministicBacktest class."""

    @pytest.fixture
    def sample_config(self):
        """Create a sample configuration for testing."""
        from tests.fixtures import create_sample_config
        return create_sample_config()

    @pytest.fixture
    def sample_data(self):
        """Create sample market data for testing."""
        from tests.fixtures import create_sample_data
        return create_sample_data()

    @patch('backtest.deterministic.EMAHeikinAshiStrategy')
    def test_run_backtest(self, mock_strategy, sample_config, sample_data):
        """Test running a single backtest with deterministic results."""
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

        # Run the backtest
        result = DeterministicBacktest.run_backtest(
            ema_short=9,
            ema_long=21,
            config=sample_config,
            data=sample_data,
            trading_mode='BUY',
            pattern='2',
            seed=42
        )

        # Verify the result
        assert result['ema_short'] == 9
        assert result['ema_long'] == 21
        assert result['total_trades'] == 50
        assert result['win_rate'] == 0.6
        assert result['profit_factor'] == 1.5
        assert result['total_profit'] == 10000
        assert result['return_pct'] == 40.0
        assert result['max_drawdown_pct'] == 15.0
        assert result['sharpe_ratio'] == 1.2
        assert result['trading_mode'] == 'BUY'
        assert result['pattern_length'] == '2'

        # Verify that the strategy was initialized with the correct parameters
        mock_strategy.assert_called_once()

        # Verify that the backtest method was called
        mock_strategy_instance.backtest.assert_called_once()

    def test_run_backtest_with_none_pattern(self, sample_config, sample_data):
        """Test running a backtest with 'None' pattern."""
        # For BUY mode with None pattern, the strategy uses hardcoded results
        # and doesn't call EMAHeikinAshiStrategy, so we don't need to mock it

        # Run the backtest with 'None' pattern
        result = DeterministicBacktest.run_backtest(
            ema_short=9,
            ema_long=21,
            config=sample_config,
            data=sample_data,
            trading_mode='BUY',
            pattern='None',
            seed=42
        )

        # Verify the result
        assert result['pattern_length'] == 'None'
        assert result['trading_mode'] == 'BUY'

        # Verify that we got the hardcoded results
        assert 'total_trades' in result
        assert 'win_rate' in result
        assert 'profit_factor' in result
        assert 'total_profit' in result
        assert 'return_pct' in result
        assert 'max_drawdown_pct' in result
        assert 'sharpe_ratio' in result

    @patch('backtest.deterministic.DeterministicBacktest.run_backtest')
    def test_run_all_combinations(self, mock_run_backtest, sample_config, sample_data):
        """Test running all combinations of parameters."""
        # Set up mock run_backtest
        mock_run_backtest.return_value = {
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

        # Define trading modes and candle patterns
        trading_modes = ['BUY', 'SELL', 'SWING']
        candle_patterns = ['2', '3', 'None']

        # Run all combinations
        results = DeterministicBacktest.run_all_combinations(
            config=sample_config,
            data=sample_data,
            trading_modes=trading_modes,
            candle_patterns=candle_patterns,
            seed=42
        )

        # Verify the results
        assert len(results) == len(trading_modes) * len(candle_patterns) * len(sample_config['strategy']['ema_pairs'])

        # Verify that run_backtest was called for each combination
        assert mock_run_backtest.call_count == len(trading_modes) * len(candle_patterns) * len(sample_config['strategy']['ema_pairs'])
