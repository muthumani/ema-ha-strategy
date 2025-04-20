"""
Tests for the patterns module functions.
"""

import pandas as pd
import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from patterns.patterns import detect_consecutive_candles, apply_ha_pattern_filter

def test_patterns_functions():
    """Test that patterns functions work correctly"""
    # Create a simple DataFrame
    df = pd.DataFrame({
        'HA_Open': [1, 2, 3, 4, 5],
        'HA_Close': [2, 3, 4, 5, 6]
    })
    
    # Test detect_consecutive_candles
    result = detect_consecutive_candles(df, 'bullish', 2)
    assert isinstance(result, pd.Series)
    
    # Test apply_ha_pattern_filter
    config = {
        'strategy': {
            'ha_patterns': {
                'enabled': True,
                'confirmation_candles': [2]
            }
        }
    }
    filtered_df = apply_ha_pattern_filter(df, config)
    assert isinstance(filtered_df, pd.DataFrame)
