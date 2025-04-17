"""
Constants module for the EMA Heikin Ashi Strategy.

This module contains default values and constants used throughout the project.
These values are used as fallbacks when not specified in the configuration file.
"""

# Default paths
DEFAULT_CONFIG_PATH = 'config/config.yaml'
DEFAULT_DATA_FOLDER = 'data/market_data'
DEFAULT_RESULTS_FOLDER = 'data/results'
DEFAULT_REPORTS_FOLDER = 'data/reports'

# Default trading parameters
DEFAULT_SYMBOL = 'NIFTY'
DEFAULT_TIMEFRAME = '1min'
DEFAULT_INITIAL_CAPITAL = 25000
DEFAULT_POSITION_SIZE = 1.0
DEFAULT_COMMISSION_PCT = 0.05
DEFAULT_SLIPPAGE_PCT = 0.02

# Default trading session times
DEFAULT_MARKET_OPEN = '09:15'
DEFAULT_MARKET_ENTRY = '09:30'
DEFAULT_FORCE_EXIT = '15:15'
DEFAULT_MARKET_CLOSE = '15:30'

# Default risk management parameters
DEFAULT_STOP_LOSS_PCT = 1.0
DEFAULT_TRAILING_STOP_PCT = 0.5
DEFAULT_USE_STOP_LOSS = True
DEFAULT_USE_TRAILING_STOP = True
DEFAULT_MAX_TRADES_PER_DAY = 5
DEFAULT_MAX_RISK_PER_TRADE = 2.0

# Default strategy parameters
DEFAULT_EMA_PAIRS = [[9, 21], [13, 34], [21, 55]]
DEFAULT_TRADING_MODES = ['SWING', 'BUY', 'SELL']
DEFAULT_CANDLE_PATTERNS = [2, 3, 'None']

# Default execution parameters
DEFAULT_EXECUTION_MODE = 'standard'
DEFAULT_SEED = 42
DEFAULT_HEALTH_PORT = 8080

# Default date range for reports (fallback when actual data not available)
DEFAULT_BACKTEST_START_DATE = '2015-01-01 09:15:00'
DEFAULT_BACKTEST_END_DATE = '2025-04-17 15:29:00'
