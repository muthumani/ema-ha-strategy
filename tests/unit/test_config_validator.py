"""
Tests for the configuration validator.
"""

import pytest
import os
from pathlib import Path
import tempfile
import yaml

import os
import sys

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.config_validator import validate_config

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

def test_validate_config_file_functionality(tmp_path):
    """Test validating a configuration file functionality"""
    # Create a temporary valid config file
    valid_config_path = tmp_path / "valid_config.yaml"
    with open(valid_config_path, "w") as f:
        yaml.dump(VALID_CONFIG, f)

    # Create a temporary invalid config file with missing required fields
    invalid_config = {}
    invalid_config_path = tmp_path / "invalid_config.yaml"
    with open(invalid_config_path, "w") as f:
        yaml.dump(invalid_config, f)

    # Create a simple validate_config_file function for testing
    def validate_config_file(config_path):
        try:
            from backtest_utils import load_config
            config = load_config(config_path)
            return validate_config(config)
        except Exception:
            return False

    # Test valid configuration file
    assert validate_config_file(valid_config_path) is True

    # Test non-existent file
    assert validate_config_file(tmp_path / "non_existent_file.yaml") is False

    # Test invalid configuration file
    assert validate_config_file(invalid_config_path) is False
