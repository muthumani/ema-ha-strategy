"""
Common test fixtures for the EMA-HA strategy tests.
"""

import pytest
import pandas as pd
import numpy as np

def create_sample_config():
    """Create a sample configuration for testing."""
    return {
        'strategy': {
            'ema_pairs': [[9, 21], [13, 34], [21, 55]],
            'trading': {
                'mode': ['SWING']
            },
            'ha_patterns': {
                'enabled': True,
                'confirmation_candles': [2]
            },
            'trading_session': {
                'market_open': '09:15:00',
                'market_entry': '09:20:00',
                'force_exit': '15:15:00',
                'market_close': '15:30:00'
            }
        },
        'backtest': {
            'initial_capital': 25000
        },
        'data': {
            'data_folder': 'data/market_data',
            'results_folder': 'data/results',
            'timeframe': '1min'
        },
        'risk_management': {
            'use_stop_loss': True,
            'stop_loss_pct': 1.0,
            'use_trailing_stop': True,
            'trailing_stop_pct': 0.5
        }
    }

def create_sample_data():
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
