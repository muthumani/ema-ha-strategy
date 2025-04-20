"""
Tests for the pattern recognition module.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import tempfile

import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import patterns.patterns
from patterns.patterns import detect_consecutive_candles, apply_ha_pattern_filter

def create_sample_data():
    """Create sample data for testing"""
    # Create date range
    dates = pd.date_range(start='2023-01-01', periods=10, freq='1min')

    # Create sample data with alternating bullish and bearish candles
    data = pd.DataFrame({
        'open': [100, 102, 103, 101, 99, 98, 100, 102, 103, 101],
        'high': [105, 106, 107, 105, 103, 102, 105, 106, 107, 105],
        'low': [98, 100, 101, 98, 97, 96, 98, 100, 101, 98],
        'close': [102, 103, 104, 99, 98, 97, 102, 103, 104, 99],
        'volume': [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900]
    }, index=dates)

    # Add Heikin Ashi columns
    data['HA_Open'] = np.nan
    data['HA_High'] = np.nan
    data['HA_Low'] = np.nan
    data['HA_Close'] = np.nan

    # Calculate first Heikin Ashi candle
    data.loc[data.index[0], 'HA_Open'] = (data.loc[data.index[0], 'open'] + data.loc[data.index[0], 'close']) / 2
    data.loc[data.index[0], 'HA_Close'] = (data.loc[data.index[0], 'open'] + data.loc[data.index[0], 'high'] +
                                          data.loc[data.index[0], 'low'] + data.loc[data.index[0], 'close']) / 4
    data.loc[data.index[0], 'HA_High'] = data.loc[data.index[0], 'high']
    data.loc[data.index[0], 'HA_Low'] = data.loc[data.index[0], 'low']

    # Calculate remaining Heikin Ashi candles
    for i in range(1, len(data)):
        data.loc[data.index[i], 'HA_Open'] = (data.loc[data.index[i-1], 'HA_Open'] + data.loc[data.index[i-1], 'HA_Close']) / 2
        data.loc[data.index[i], 'HA_Close'] = (data.loc[data.index[i], 'open'] + data.loc[data.index[i], 'high'] +
                                              data.loc[data.index[i], 'low'] + data.loc[data.index[i], 'close']) / 4
        data.loc[data.index[i], 'HA_High'] = max(data.loc[data.index[i], 'high'], data.loc[data.index[i], 'HA_Open'], data.loc[data.index[i], 'HA_Close'])
        data.loc[data.index[i], 'HA_Low'] = min(data.loc[data.index[i], 'low'], data.loc[data.index[i], 'HA_Open'], data.loc[data.index[i], 'HA_Close'])

    return data

def test_detect_consecutive_candles():
    """Test detection of consecutive candles"""
    # Create sample data
    data = create_sample_data()

    # Test bullish pattern detection with 2 candles
    bullish_pattern_2 = detect_consecutive_candles(data, 'bullish', 2)
    assert isinstance(bullish_pattern_2, pd.Series)
    assert len(bullish_pattern_2) == len(data)

    # Test bearish pattern detection with 2 candles
    bearish_pattern_2 = detect_consecutive_candles(data, 'bearish', 2)
    assert isinstance(bearish_pattern_2, pd.Series)
    assert len(bearish_pattern_2) == len(data)

    # Test bullish pattern detection with 3 candles
    bullish_pattern_3 = detect_consecutive_candles(data, 'bullish', 3)
    assert isinstance(bullish_pattern_3, pd.Series)
    assert len(bullish_pattern_3) == len(data)

    # Test bearish pattern detection with 3 candles
    bearish_pattern_3 = detect_consecutive_candles(data, 'bearish', 3)
    assert isinstance(bearish_pattern_3, pd.Series)
    assert len(bearish_pattern_3) == len(data)

    # Test invalid pattern type
    with pytest.raises(ValueError):
        detect_consecutive_candles(data, 'invalid', 2)

    # Test invalid length
    with pytest.raises(ValueError):
        detect_consecutive_candles(data, 'bullish', 4)

    # Test error handling with missing columns
    data_missing_columns = data.drop(columns=['HA_Open', 'HA_Close'])
    result = detect_consecutive_candles(data_missing_columns, 'bullish', 2)
    assert isinstance(result, pd.Series)
    assert len(result) == len(data_missing_columns)
    assert not result.any()  # All values should be False

def test_apply_ha_pattern_filter():
    """Test applying Heikin Ashi pattern filter"""
    # Create sample data
    data = create_sample_data()

    # Create sample config
    config = {
        'strategy': {
            'ha_patterns': {
                'enabled': True,
                'confirmation_candles': [2]
            }
        }
    }

    # Test with default config
    filtered_data = apply_ha_pattern_filter(data, config)
    assert 'Bullish_Pattern' in filtered_data.columns
    assert 'Bearish_Pattern' in filtered_data.columns

    # Test with specified candle pattern
    filtered_data_3 = apply_ha_pattern_filter(data, config, candle_pattern=3)
    assert 'Bullish_Pattern' in filtered_data_3.columns
    assert 'Bearish_Pattern' in filtered_data_3.columns

    # Test with None candle pattern
    config_none = {
        'strategy': {
            'ha_patterns': {
                'enabled': True,
                'confirmation_candles': ['None']
            }
        }
    }
    filtered_data_none = apply_ha_pattern_filter(data, config_none)
    # The function returns the original DataFrame without adding pattern columns
    # but it doesn't remove existing columns, so we just check that the function returns a DataFrame
    assert isinstance(filtered_data_none, pd.DataFrame)

    # Test with None candle pattern from command line
    filtered_data_none_cmd = apply_ha_pattern_filter(data, config, candle_pattern="None")
    # The function returns the original DataFrame without modifying it
    assert isinstance(filtered_data_none_cmd, pd.DataFrame)

    # Test with invalid candle pattern
    with pytest.raises(ValueError):
        apply_ha_pattern_filter(data, config, candle_pattern=4)

    # Test with empty confirmation candles
    config_empty = {
        'strategy': {
            'ha_patterns': {
                'enabled': True,
                'confirmation_candles': []
            }
        }
    }
    filtered_data_empty = apply_ha_pattern_filter(data, config_empty)
    assert isinstance(filtered_data_empty, pd.DataFrame)
    assert filtered_data_empty is data  # Should return the original DataFrame

    # Test with missing ha_patterns in config
    config_missing = {
        'strategy': {}
    }
    filtered_data_missing = apply_ha_pattern_filter(data, config_missing)
    assert isinstance(filtered_data_missing, pd.DataFrame)
    assert filtered_data_missing is data  # Should return the original DataFrame

    # Test error handling with missing columns
    data_missing_columns = data.drop(columns=['HA_Open', 'HA_Close'])
    result = apply_ha_pattern_filter(data_missing_columns, config)
    assert isinstance(result, pd.DataFrame)

    # Test error handling with invalid candle pattern exception propagation
    # Create a mock function that raises a ValueError with the specific message
    def mock_detect_consecutive_candles_value_error(df, pattern_type, length):
        raise ValueError("Invalid candle pattern length: 4. Must be 2, 3, or None.")

    # Save the original function
    original_detect = patterns.patterns.detect_consecutive_candles

    try:
        # Replace the function with our mock
        patterns.patterns.detect_consecutive_candles = mock_detect_consecutive_candles_value_error

        # This should re-raise the ValueError
        with pytest.raises(ValueError, match="Invalid candle pattern length"):
            apply_ha_pattern_filter(data, config)
    finally:
        # Restore the original function
        patterns.patterns.detect_consecutive_candles = original_detect

    # Test error handling with other exceptions
    # Create a mock function that raises a different exception
    def mock_detect_consecutive_candles_other_error(df, pattern_type, length):
        raise KeyError("Some other error")

    try:
        # Replace the function with our mock
        patterns.patterns.detect_consecutive_candles = mock_detect_consecutive_candles_other_error

        # This should catch the exception and return the original DataFrame
        result = apply_ha_pattern_filter(data, config)
        assert result is data  # Should return the original DataFrame
    finally:
        # Restore the original function
        patterns.patterns.detect_consecutive_candles = original_detect
