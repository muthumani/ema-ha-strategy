"""
Heikin Ashi pattern recognition module.

This module provides functions to identify various Heikin Ashi candlestick patterns
that can be used as confirmation signals in trading strategies.

This is a compatibility layer that imports from utils.patterns.
"""

import logging
from logger import setup_logger
from utils.patterns import detect_consecutive_candles, apply_ha_pattern_filter

# Set up logger
logger = setup_logger(name="ha_patterns", log_level=logging.INFO)
logger.info("Using ha_patterns module (deprecated, use utils.patterns instead)")
