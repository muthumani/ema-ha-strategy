"""
Tests for the backtest.runner module.
"""

import pytest
import os
from unittest.mock import patch, MagicMock

# Add the project root directory to the Python path
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backtest.runner import format_results_table, find_best_pair, analyze_exit_reasons, print_backtest_summary, main

class TestRunner:
    """Test cases for backtest.runner module."""
    
    @pytest.fixture
    def sample_results(self):
        """Create sample backtest results for testing."""
        return [
            {
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
                'monthly_returns_avg': 4.0,
                'monthly_returns_std': 1.5
            }
        ]
    
    @pytest.fixture
    def sample_trades(self):
        """Create sample trades for testing."""
        return [
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
    
    def test_format_results_table(self, sample_results):
        """Test formatting backtest results into a table."""
        # Format the results table
        table = format_results_table(sample_results)
        
        # Verify the table is a string
        assert isinstance(table, str)
        
        # Verify the table contains the expected data
        assert '9/21' in table
        assert '13/34' in table
        assert '50' in table
        assert '40' in table
        assert '60.0' in table
    
    def test_find_best_pair(self, sample_results):
        """Test finding the best performing EMA pair."""
        # Find the best pair
        best_pair = find_best_pair(sample_results)
        
        # Verify the best pair
        assert best_pair['ema_pair'] == '13/34'
        assert best_pair['return_pct'] == 60.0
        assert best_pair['sharpe'] == 4.0 / 1.5
        assert best_pair['win_rate'] == 0.7
        assert best_pair['profit_factor'] == 2.0
    
    def test_analyze_exit_reasons(self, sample_trades):
        """Test analyzing trade exit reasons."""
        # Analyze exit reasons
        exit_stats = analyze_exit_reasons(sample_trades)
        
        # Verify the exit stats
        assert exit_stats['signal_exits_pct'] == 50.0
        assert exit_stats['force_exits_pct'] == 50.0
    
    @patch('builtins.print')
    def test_print_backtest_summary(self, mock_print, sample_results, sample_trades):
        """Test printing a detailed backtest summary."""
        # Print the summary
        print_backtest_summary(sample_results[0], sample_trades)
        
        # Verify that print was called
        assert mock_print.call_count > 0
    
    @patch('backtest.runner.load_config')
    @patch('backtest.runner.load_data')
    @patch('backtest.runner.EMAHeikinAshiStrategy')
    @patch('backtest.runner.save_results')
    @patch('backtest.runner.format_results_table')
    @patch('backtest.runner.find_best_pair')
    @patch('builtins.print')
    def test_main(self, mock_print, mock_find_best_pair, mock_format_results_table, 
                 mock_save_results, mock_strategy, mock_load_data, mock_load_config):
        """Test the main function."""
        # Set up mock load_config
        mock_load_config.return_value = {
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
        
        # Set up mock load_data
        mock_data = MagicMock()
        mock_data.attrs = {
            'start_date': '2023-01-01 09:15:00',
            'end_date': '2023-01-31 15:30:00',
            'total_days': 21,
            'total_candles': 8400
        }
        mock_load_data.return_value = mock_data
        
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
                'monthly_returns_avg': 3.0,
                'monthly_returns_std': 2.0
            },
            []  # trades
        )
        mock_strategy.return_value = mock_strategy_instance
        
        # Set up mock format_results_table
        mock_format_results_table.return_value = "Formatted table"
        
        # Set up mock find_best_pair
        mock_find_best_pair.return_value = {
            'ema_pair': '9/21',
            'return_pct': 40.0,
            'sharpe': 1.5,
            'win_rate': 0.6,
            'profit_factor': 1.5
        }
        
        # Run main
        main()
        
        # Verify that load_config was called
        mock_load_config.assert_called_once()
        
        # Verify that load_data was called
        mock_load_data.assert_called_once()
        
        # Verify that the strategy was initialized for each EMA pair
        assert mock_strategy.call_count == 2
        
        # Verify that backtest was called for each EMA pair
        assert mock_strategy_instance.backtest.call_count == 2
        
        # Verify that save_results was called for each EMA pair
        assert mock_save_results.call_count == 2
        
        # Verify that format_results_table was called
        mock_format_results_table.assert_called_once()
        
        # Verify that find_best_pair was called
        mock_find_best_pair.assert_called_once()
        
        # Verify that print was called multiple times
        assert mock_print.call_count > 0
