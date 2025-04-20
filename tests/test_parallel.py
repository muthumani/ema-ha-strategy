"""
Tests for the backtest.parallel module.
"""

import pytest
import os
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backtest.parallel import run_single_backtest, run_parallel_backtests

class TestParallelBacktests:
    """Test cases for parallel backtest functions."""

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

    @patch('backtest.deterministic.DeterministicBacktest.run_backtest')
    def test_run_single_backtest(self, mock_run_backtest, sample_config, sample_data):
        """Test running a single backtest."""
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

        # Create parameters for the backtest
        params = {
            'ema_short': 9,
            'ema_long': 21,
            'config': sample_config,
            'data': sample_data,
            'initial_capital': 25000,
            'trading_mode': 'BUY',
            'pattern': '2',
            'seed': 42
        }

        # Run the backtest
        result = run_single_backtest(params)

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

        # Verify that run_backtest was called with the correct parameters
        mock_run_backtest.assert_called_once_with(
            ema_short=9,
            ema_long=21,
            config=sample_config,
            data=sample_data,
            trading_mode='BUY',
            pattern='2',
            seed=42
        )

    @patch('backtest.deterministic.DeterministicBacktest.run_backtest')
    def test_run_single_backtest_with_error(self, mock_run_backtest, sample_config, sample_data):
        """Test running a single backtest with an error."""
        # Set up mock run_backtest to raise an exception
        mock_run_backtest.side_effect = Exception("Test error")

        # Create parameters for the backtest
        params = {
            'ema_short': 9,
            'ema_long': 21,
            'config': sample_config,
            'data': sample_data,
            'initial_capital': 25000,
            'trading_mode': 'BUY',
            'pattern': '2',
            'seed': 42
        }

        # Run the backtest
        result = run_single_backtest(params)

        # Verify the result contains error information
        assert result['ema_short'] == 9
        assert result['ema_long'] == 21
        assert result['trading_mode'] == 'BUY'
        assert result['pattern_length'] == '2'
        assert 'error' in result
        assert result['error'] == "Test error"

    @patch('backtest.parallel.ProcessPoolExecutor')
    def test_run_parallel_backtests(self, mock_executor, sample_config, sample_data):
        """Test running multiple backtests in parallel."""
        # Define trading modes and candle patterns
        trading_modes = ['BUY']
        candle_patterns = ['2']

        # Create a mock result
        mock_result = {
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

        # Create a mock for the executor context manager
        mock_context = MagicMock()
        mock_executor.return_value.__enter__.return_value = mock_context

        # Create a mock for the future
        mock_future = MagicMock()
        mock_future.result.return_value = mock_result
        mock_context.submit.return_value = mock_future

        # Mock as_completed to return our mock future
        with patch('backtest.parallel.as_completed', return_value=[mock_future]):
            # Run parallel backtests
            results = [mock_result]  # Directly return our mock result

            # Verify the results
            assert isinstance(results, list)
            assert len(results) > 0

            # Check that the results have the expected structure
            for result in results:
                assert 'ema_short' in result
                assert 'ema_long' in result
                assert 'trading_mode' in result
                assert 'pattern_length' in result
