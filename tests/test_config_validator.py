"""
Tests for the configuration validator.
"""

import pytest
import os
from pathlib import Path
import tempfile
import yaml

from utils.config_validator import validate_config, validate_config_file

# Sample valid configuration for testing
VALID_CONFIG = {
    "strategy": {
        "ema_pairs": [[9, 21], [13, 34], [50, 200]],
        "trading": {
            "mode": ["SWING"]
        },
        "ha_patterns": {
            "enabled": True,
            "confirmation_candles": [2]
        }
    },
    "backtest": {
        "initial_capital": 100000,
        "commission": 0.0,
        "slippage": 0.0
    },
    "data": {
        "data_folder": "data/market_data",
        "results_folder": "data/results",
        "timeframe": "1min"
    },
    "logging": {
        "level": "INFO"
    }
}

def test_validate_config_valid():
    """Test that a valid configuration passes validation"""
    assert validate_config(VALID_CONFIG) is True

def test_validate_config_missing_required():
    """Test that a configuration missing required fields fails validation"""
    # Missing strategy
    invalid_config = VALID_CONFIG.copy()
    invalid_config.pop("strategy")
    assert validate_config(invalid_config) is False

    # Missing backtest
    invalid_config = VALID_CONFIG.copy()
    invalid_config.pop("backtest")
    assert validate_config(invalid_config) is False

    # Missing data
    invalid_config = VALID_CONFIG.copy()
    invalid_config.pop("data")
    assert validate_config(invalid_config) is False

def test_validate_config_invalid_values():
    """Test that a configuration with invalid values fails validation"""
    # Invalid EMA pairs (negative value)
    invalid_config = VALID_CONFIG.copy()
    invalid_config["strategy"] = VALID_CONFIG["strategy"].copy()
    invalid_config["strategy"]["ema_pairs"] = [[-1, 21]]
    assert validate_config(invalid_config) is False

    # Invalid trading mode
    invalid_config = VALID_CONFIG.copy()
    invalid_config["strategy"] = VALID_CONFIG["strategy"].copy()
    invalid_config["strategy"]["trading"] = {"mode": ["INVALID"]}
    assert validate_config(invalid_config) is False

    # Invalid initial capital (negative)
    invalid_config = VALID_CONFIG.copy()
    invalid_config["backtest"] = VALID_CONFIG["backtest"].copy()
    invalid_config["backtest"]["initial_capital"] = -1000
    assert validate_config(invalid_config) is False

def test_validate_config_file():
    """Test validating a configuration file"""
    # Create a temporary file with valid configuration
    with tempfile.NamedTemporaryFile(suffix='.yaml', mode='w', delete=False, encoding='utf-8') as temp:
        yaml.dump(VALID_CONFIG, temp)
        temp_path = temp.name

    try:
        # Test valid configuration file
        assert validate_config_file(temp_path) is True

        # Test non-existent file
        assert validate_config_file("non_existent_file.yaml") is False

        # Test invalid configuration file
        with open(temp_path, 'w') as f:
            f.write("invalid: yaml: content")
        assert validate_config_file(temp_path) is False
    finally:
        # Clean up
        os.unlink(temp_path)
