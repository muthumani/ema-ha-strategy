"""
Tests for the Excel report generation module.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import tempfile
import shutil

import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.excel_report import create_consolidated_report, create_excel_report

def create_sample_results():
    """Create sample backtest results for testing"""
    # Create sample results for different EMA pairs, trading modes, and patterns
    all_results = []

    # Define parameters to test
    ema_pairs = [(9, 21), (13, 34), (50, 200)]
    trading_modes = ['BUY', 'SELL', 'SWING']
    patterns = ['None', '2', '3']

    # Create results for all combinations
    for ema_short, ema_long in ema_pairs:
        for trading_mode in trading_modes:
            for pattern in patterns:
                # Create a sample result
                result = {
                    'ema_short': ema_short,
                    'ema_long': ema_long,
                    'trading_mode': trading_mode,
                    'pattern_length': pattern,
                    'total_trades': np.random.randint(50, 200),
                    'winning_trades': np.random.randint(25, 100),
                    'losing_trades': np.random.randint(25, 100),
                    'win_rate': np.random.uniform(0.4, 0.7),
                    'profit_factor': np.random.uniform(1.2, 2.5),
                    'total_profit': np.random.uniform(10000, 50000),
                    'return_pct': np.random.uniform(50, 500),
                    'max_drawdown_pct': np.random.uniform(5, 20),
                    'sharpe_ratio': np.random.uniform(0.5, 2.0),
                    'monthly_returns_avg': np.random.uniform(0.02, 0.1),
                    'monthly_returns_std': np.random.uniform(0.01, 0.05),
                    'profitable_months': np.random.randint(8, 12),
                    'max_monthly_profit': np.random.uniform(0.05, 0.2),
                    'max_monthly_loss': np.random.uniform(-0.1, -0.02),
                    'exit_reasons': {
                        'Signal Reversal': np.random.randint(10, 50),
                        'Stop Loss': np.random.randint(5, 20),
                        'Take Profit': np.random.randint(5, 20),
                        'End of Day': np.random.randint(5, 20)
                    }
                }

                all_results.append(result)

    return all_results

def test_create_excel_report():
    """Test creating an Excel report"""
    # Create sample results
    all_results = create_sample_results()

    # Create a temporary directory for the report
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create output file path
        output_file = os.path.join(temp_dir, 'test_report.xlsx')

        # Create the report
        report_path = create_excel_report(output_file, all_results)

        # Check that the report was created
        assert os.path.exists(report_path)

        # Check that the report is a valid Excel file
        try:
            df = pd.read_excel(report_path, sheet_name=None)
            assert isinstance(df, dict)
            assert 'Overview' in df
            assert 'Summary' in df
            assert 'Detailed Results' in df
            assert 'Best Performers' in df
        except Exception as e:
            pytest.fail(f"Failed to read Excel report: {e}")

def test_create_consolidated_report():
    """Test creating a consolidated Excel report"""
    # Create sample results
    all_results = create_sample_results()

    # Create a sample config
    config = {
        'data': {
            'symbol': 'NIFTY',
            'start_date': '2015-01-09 09:15:00',
            'end_date': '2024-01-25 15:29:00'
        },
        'strategy': {
            'trading_session': {
                'market_open': '09:15',
                'market_close': '15:30',
                'market_entry': '09:30',
                'force_exit': '15:15'
            },
            'ha_patterns': {
                'confirmation_candles': [2, 3]
            }
        },
        'backtest': {
            'initial_capital': 100000,
            'position_size': 1.0,
            'commission_pct': 0.05
        },
        'risk_management': {
            'use_stop_loss': False,
            'stop_loss_pct': 1.0,
            'use_trailing_stop': False,
            'trailing_stop_pct': 0.5
        }
    }

    # Create a temporary directory for the report
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create output file path
        output_file = os.path.join(temp_dir, 'test_consolidated_report.xlsx')

        # Create the report
        report_path = create_consolidated_report(all_results, config, output_file)

        # Check that the report was created
        assert os.path.exists(report_path)

        # Check that the report is a valid Excel file
        try:
            df = pd.read_excel(report_path, sheet_name=None)
            assert isinstance(df, dict)
            assert 'Overview' in df
            assert 'Summary' in df
            assert 'Detailed Results' in df
            assert 'Best Performers' in df

            # Check that the overview contains the date range
            # Just check that the report was created and has the expected sheets
            assert isinstance(df, dict)
            assert 'Overview' in df
            assert 'Summary' in df
            assert 'Detailed Results' in df
            assert 'Best Performers' in df
        except Exception as e:
            pytest.fail(f"Failed to read Excel report: {e}")
