"""
Configuration validator for the EMA Heikin Ashi Strategy.
Validates the configuration file against a schema.
"""

import logging
from typing import Dict, Any, List, Optional, Union
import jsonschema
from jsonschema import validate
from pathlib import Path

from utils.logger import setup_logger

# Set up logger
logger = setup_logger(name="config_validator", log_level=logging.INFO)

# Define the schema for the configuration file
CONFIG_SCHEMA = {
    "type": "object",
    "required": ["strategy", "backtest", "data", "logging"],
    "properties": {
        "strategy": {
            "type": "object",
            "required": ["ema_pairs", "trading"],
            "properties": {
                "ema_pairs": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "minItems": 2,
                        "maxItems": 2,
                        "items": {"type": "integer", "minimum": 1}
                    },
                    "minItems": 1
                },
                "trading": {
                    "type": "object",
                    "required": ["mode"],
                    "properties": {
                        "mode": {
                            "type": "array",
                            "items": {"type": "string", "enum": ["BUY", "SELL", "SWING"]},
                            "minItems": 1
                        }
                    }
                },
                "ha_patterns": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "confirmation_candles": {
                            "type": "array",
                            "items": {"type": ["integer", "null", "string"], "enum": [2, 3, None, "None"]},
                            "minItems": 1
                        }
                    }
                }
            }
        },
        "backtest": {
            "type": "object",
            "required": ["initial_capital"],
            "properties": {
                "initial_capital": {"type": "number", "minimum": 0},
                "commission": {"type": "number", "minimum": 0},
                "slippage": {"type": "number", "minimum": 0}
            }
        },
        "data": {
            "type": "object",
            "required": ["data_folder", "results_folder", "timeframe"],
            "properties": {
                "data_folder": {"type": "string"},
                "results_folder": {"type": "string"},
                "timeframe": {"type": "string"},
                "start_date": {"type": "string", "format": "date-time"},
                "end_date": {"type": "string", "format": "date-time"}
            }
        },
        "logging": {
            "type": "object",
            "properties": {
                "level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
                "file": {"type": "string"}
            }
        }
    }
}

def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate the configuration against the schema.

    Args:
        config: Configuration dictionary

    Returns:
        True if the configuration is valid, False otherwise
    """
    try:
        validate(instance=config, schema=CONFIG_SCHEMA)
        logger.info("Configuration validation successful")
        return True
    except jsonschema.exceptions.ValidationError as e:
        logger.error(f"Configuration validation failed: {e}")
        return False

def validate_config_file(config_path: Union[str, Path]) -> bool:
    """
    Validate a configuration file against the schema.

    Args:
        config_path: Path to the configuration file

    Returns:
        True if the configuration is valid, False otherwise
    """
    from backtest.utils import load_config

    try:
        config = load_config(config_path)
        return validate_config(config)
    except Exception as e:
        logger.error(f"Error loading configuration file: {e}")
        return False
