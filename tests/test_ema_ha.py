"""
Tests for the EMA Heikin Ashi strategy
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.ema_ha import EMAHeikinAshiStrategy
from backtest.utils import load_config

# Create a fixture for test data
@pytest.fixture
def sample_data():
    """Create sample OHLC data for testing"""
    # Create date range
    start_date = datetime(2023, 1, 1, 9, 15)
    dates = [start_date + timedelta(minutes=i) for i in range(1000)]

    # Create price data with a trend
    close_prices = np.linspace(100, 120, 1000) + np.sin(np.linspace(0, 20, 1000)) * 5

    # Add some noise
    close_prices = close_prices + np.random.normal(0, 1, 1000)

    # Create OHLC data
    high_prices = close_prices + np.random.uniform(0, 2, 1000)
    low_prices = close_prices - np.random.uniform(0, 2, 1000)
    open_prices = close_prices - np.random.uniform(-1, 1, 1000)

    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices
    })

    # Set date as index
    df.set_index('date', inplace=True)

    return df

# Create a fixture for test config
@pytest.fixture
def sample_config():
    """Create sample configuration for testing"""
    return {
        'strategy': {
            'ema_pairs': [[9, 21], [13, 34]],
            'trading_session': {
                'market_open': '09:15',
                'market_entry': '09:30',
                'force_exit': '15:15',
                'market_close': '15:30'
            }
        },
        'risk_management': {
            'use_stop_loss': True,
            'stop_loss_pct': 1.0,
            'use_trailing_stop': True,
            'trailing_stop_pct': 0.5
        },
        'backtest': {
            'initial_capital': 25000,
            'position_size': 1.0
        }
    }

def test_strategy_initialization(sample_config):
    """Test strategy initialization"""
    # Test valid initialization
    strategy = EMAHeikinAshiStrategy(9, 21, sample_config)
    assert strategy.ema_short == 9
    assert strategy.ema_long == 21
    assert strategy.use_stop_loss == True
    assert strategy.stop_loss_pct == 1.0

    # Test invalid initialization (short EMA >= long EMA)
    with pytest.raises(ValueError):
        EMAHeikinAshiStrategy(21, 9, sample_config)

    # Test missing configuration
    with pytest.raises(ValueError):
        EMAHeikinAshiStrategy(9, 21, {})

def test_calculate_ema(sample_data):
    """Test EMA calculation"""
    strategy = EMAHeikinAshiStrategy(9, 21, {'strategy': {'trading_session': {
        'market_open': '09:15',
        'market_entry': '09:30',
        'force_exit': '15:15',
        'market_close': '15:30'
    }}})

    # Calculate EMA
    ema9 = strategy.calculate_ema(sample_data['close'], 9)
    ema21 = strategy.calculate_ema(sample_data['close'], 21)

    # Check that EMAs have the correct length
    assert len(ema9) == len(sample_data)
    assert len(ema21) == len(sample_data)

    # Check that EMAs are different
    assert not ema9.equals(ema21)

    # Check that EMAs are close to close price (should lag)
    assert abs(ema9.iloc[-1] - sample_data['close'].iloc[-1]) < 5
    assert abs(ema21.iloc[-1] - sample_data['close'].iloc[-1]) < 5

def test_calculate_heikin_ashi(sample_data):
    """Test Heikin Ashi calculation"""
    strategy = EMAHeikinAshiStrategy(9, 21, {'strategy': {'trading_session': {
        'market_open': '09:15',
        'market_entry': '09:30',
        'force_exit': '15:15',
        'market_close': '15:30'
    }}})

    # Calculate Heikin Ashi
    ha_open, ha_close = strategy.calculate_heikin_ashi(sample_data)

    # Check that HA series have the correct length
    assert len(ha_open) == len(sample_data)
    assert len(ha_close) == len(sample_data)

    # Check that HA close is the average of OHLC
    expected_ha_close = (sample_data['open'] + sample_data['high'] +
                         sample_data['low'] + sample_data['close']) / 4
    pd.testing.assert_series_equal(ha_close, expected_ha_close)

    # Check first HA open value
    expected_first_ha_open = (sample_data['open'].iloc[0] + sample_data['close'].iloc[0]) / 2
    assert ha_open.iloc[0] == expected_first_ha_open

def test_generate_signals(sample_data, sample_config):
    """Test signal generation"""
    strategy = EMAHeikinAshiStrategy(9, 21, sample_config)

    # Generate signals
    df_with_signals = strategy.generate_signals(sample_data.copy())

    # Check that signals column exists
    assert 'Signal' in df_with_signals.columns

    # Check that EMA columns exist
    assert 'EMA_Short' in df_with_signals.columns
    assert 'EMA_Long' in df_with_signals.columns

    # Check that HA columns exist
    assert 'HA_Open' in df_with_signals.columns
    assert 'HA_Close' in df_with_signals.columns

    # Check that signals are -1, 0, or 1
    assert df_with_signals['Signal'].isin([-1, 0, 1]).all()

def test_backtest(sample_data, sample_config):
    """Test backtest functionality"""
    strategy = EMAHeikinAshiStrategy(9, 21, sample_config)

    # Run backtest
    results, trades = strategy.backtest(sample_data.copy())

    # Check that results is a dictionary
    assert isinstance(results, dict)

    # Check that trades is a list
    assert isinstance(trades, list)

    # Check that results contains key metrics
    assert 'total_trades' in results
    assert 'win_rate' in results
    assert 'profit_factor' in results
    assert 'total_profit' in results
    assert 'return_pct' in results
    assert 'max_drawdown_pct' in results

    # Check that win_rate is between 0 and 1
    assert 0 <= results['win_rate'] <= 1

    # Check that trades have required fields
    if trades:
        assert 'entry_time' in trades[0]
        assert 'exit_time' in trades[0]
        assert 'entry_price' in trades[0]
        assert 'exit_price' in trades[0]
        assert 'position_type' in trades[0]
        assert 'pnl' in trades[0]
        assert 'exit_reason' in trades[0]

if __name__ == "__main__":
    pytest.main(["-xvs", __file__])
