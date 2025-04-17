"""
Configuration utilities for the EMA Heikin Ashi Strategy.

This module provides functions to access configuration values with fallbacks to constants.
"""

import logging
from typing import Any, Dict, List, Union, Optional
from pathlib import Path
import constants
from backtest_utils import load_config
from logger import setup_logger

# Set up logger
logger = setup_logger(name="config_utils", log_level=logging.INFO)

# Global configuration cache
_config_cache = None

def get_config(config_path: str = constants.DEFAULT_CONFIG_PATH) -> Dict[str, Any]:
    """
    Load configuration from yaml file with caching.

    Args:
        config_path: Path to the configuration file

    Returns:
        Dictionary containing configuration settings
    """
    global _config_cache

    if _config_cache is None:
        try:
            _config_cache = load_config(config_path)
            logger.info(f"Configuration loaded from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            logger.warning("Using default configuration values")
            _config_cache = {}

    return _config_cache

def get_config_value(key_path: str, default_value: Any = None) -> Any:
    """
    Get a configuration value by its key path with fallback to a default value.

    Args:
        key_path: Dot-separated path to the configuration value (e.g., 'data.symbol')
        default_value: Default value to return if the key is not found

    Returns:
        The configuration value or the default value if not found
    """
    config = get_config()
    keys = key_path.split('.')

    # Navigate through the config dictionary
    current = config
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            logger.debug(f"Config key '{key_path}' not found, using default: {default_value}")
            return default_value

    return current

# Specific getter functions for commonly used values

def get_symbol() -> str:
    """Get the trading symbol"""
    return get_config_value('data.symbol', constants.DEFAULT_SYMBOL)

def get_initial_capital() -> float:
    """Get the initial capital for backtesting"""
    return get_config_value('backtest.initial_capital', constants.DEFAULT_INITIAL_CAPITAL)

def get_ema_pairs() -> List[List[int]]:
    """Get the EMA pairs for backtesting"""
    return get_config_value('strategy.ema_pairs', constants.DEFAULT_EMA_PAIRS)

def get_trading_modes() -> List[str]:
    """Get the trading modes"""
    return get_config_value('strategy.trading.mode', constants.DEFAULT_TRADING_MODES)

def get_candle_patterns() -> List[Union[int, str]]:
    """Get the candle patterns"""
    return get_config_value('strategy.ha_patterns.confirmation_candles', constants.DEFAULT_CANDLE_PATTERNS)

def get_market_session_times() -> Dict[str, str]:
    """Get the market session times"""
    session = get_config_value('strategy.trading_session', {})
    return {
        'market_open': session.get('market_open', constants.DEFAULT_MARKET_OPEN),
        'market_entry': session.get('market_entry', constants.DEFAULT_MARKET_ENTRY),
        'force_exit': session.get('force_exit', constants.DEFAULT_FORCE_EXIT),
        'market_close': session.get('market_close', constants.DEFAULT_MARKET_CLOSE)
    }

def get_risk_management() -> Dict[str, Any]:
    """Get the risk management parameters"""
    risk = get_config_value('risk_management', {})
    return {
        'use_stop_loss': risk.get('use_stop_loss', constants.DEFAULT_USE_STOP_LOSS),
        'stop_loss_pct': risk.get('stop_loss_pct', constants.DEFAULT_STOP_LOSS_PCT),
        'use_trailing_stop': risk.get('use_trailing_stop', constants.DEFAULT_USE_TRAILING_STOP),
        'trailing_stop_pct': risk.get('trailing_stop_pct', constants.DEFAULT_TRAILING_STOP_PCT),
        'max_trades_per_day': risk.get('max_trades_per_day', constants.DEFAULT_MAX_TRADES_PER_DAY),
        'max_risk_per_trade': risk.get('max_risk_per_trade', constants.DEFAULT_MAX_RISK_PER_TRADE)
    }

def get_execution_settings() -> Dict[str, Any]:
    """Get the execution settings"""
    execution = get_config_value('execution', {})
    return {
        'mode': execution.get('mode', constants.DEFAULT_EXECUTION_MODE),
        'seed': execution.get('seed', constants.DEFAULT_SEED),
        'health_port': execution.get('health_port', constants.DEFAULT_HEALTH_PORT)
    }

def get_report_settings() -> Dict[str, str]:
    """Get the report settings"""
    report = get_config_value('report', {})
    return {
        'default_start_date': report.get('default_start_date', constants.DEFAULT_BACKTEST_START_DATE),
        'default_end_date': report.get('default_end_date', constants.DEFAULT_BACKTEST_END_DATE)
    }

def get_backtest_date_range() -> str:
    """Get the backtest date range string for reports"""
    settings = get_report_settings()
    return f"{settings['default_start_date']} to {settings['default_end_date']}"
