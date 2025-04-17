# EMA Heikin Ashi Strategy

A production-ready implementation of the EMA Heikin Ashi trading strategy for NIFTY Index 50.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Version

Current version: 1.0.0

## Overview

This project implements a trading strategy based on Exponential Moving Average (EMA) crossovers combined with Heikin Ashi candles. The strategy is designed for intraday trading on the NIFTY Index 50.

### Key Features

- **EMA Crossover**: Uses EMA crossovers to identify trend changes
- **Heikin Ashi Candles**: Uses Heikin Ashi candles to filter out market noise
- **Risk Management**: Implements stop loss and trailing stop mechanisms
- **Performance Metrics**: Calculates comprehensive performance metrics
- **Excel Reporting**: Generates detailed Excel reports with performance metrics
- **Multiple Trading Modes**: Support for BUY, SELL, and SWING (both) trading modes
- **Comparative Analysis**: Compare performance across different configurations
- **Configuration Validation**: Validates configuration files against a schema
- **Type Hints**: Comprehensive type annotations for better code quality
- **Test Suite**: Includes unit tests and integration tests for core components
- **Cross-Validation**: Supports deterministic and sequential execution modes for result validation
- **Parallel Processing**: Utilizes multi-core processing for faster backtesting
- **Docker Support**: Containerized deployment with Docker and Docker Compose
- **Health Check Server**: Built-in health monitoring for production deployments

## Installation

### Standard Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ema-ha-strategy.git
cd ema-ha-strategy

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### Docker Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ema-ha-strategy.git
cd ema-ha-strategy

# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ema-ha-strategy.git
cd ema-ha-strategy

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install in development mode
pip install -e .

# Install development dependencies
pip install -r requirements-dev.txt
```

## Usage

### Basic Usage

```bash
python main.py --config config/config.yaml --symbol NIFTY
```

### Running with Different Execution Modes

```bash
# Standard mode (parallel, non-deterministic)
python main.py --execution-mode standard

# Deterministic mode (parallel with fixed seed)
python main.py --execution-mode deterministic --seed 42

# Sequential mode (no parallelization, deterministic)
python main.py --execution-mode sequential

# Validation mode (quick validation before execution)
python main.py --execution-mode validate

# Cross-validation mode (full cross-validation)
python main.py --execution-mode cross-validate
```

### Comparative Analysis

```bash
# Compare trading modes (BUY, SELL, SWING)
python main.py --compare

# Compare candle patterns (2-candle, 3-candle, None)
python main.py --compare-patterns

# Run all combinations of trading modes and candle patterns
python main.py --all-combinations
```

### Generating Reports

```bash
# Generate consolidated Excel report
python main.py --report
```

### Docker Usage

```bash
# Run with default configuration
docker-compose up

# Run with custom command line arguments
docker-compose run ema-ha-strategy --execution-mode deterministic --seed 42
```

### Command Line Arguments

#### Basic Configuration
- `--config`: Path to configuration file (default: config/config.yaml)
- `--no-config`: Ignore config file and use only command-line arguments

#### Override Options
- `--data`: Path to market data file (overrides config)
- `--symbol`: Trading symbol (default: NIFTY)
- `--output`: Output directory for results (overrides config)
- `--debug`: Enable debug logging

#### Strategy Options
- `--mode`: Trading mode (BUY, SELL, SWING) to override config
- `--candle-pattern`: Number of consecutive candles required for pattern confirmation (2, 3, or None)

#### Analysis Options
- `--compare`: Run comparative analysis across all trading modes
- `--compare-patterns`: Run comparative analysis across all candle patterns
- `--all-combinations`: Run analysis for all combinations of trading modes and candle patterns
- `--report`: Generate consolidated Excel report

#### Performance and Validation Options
- `--execution-mode`: Execution mode for strategy testing (standard, deterministic, sequential, validate, cross-validate)
- `--seed`: Random seed for reproducibility when using deterministic mode

## Configuration

The strategy is configured using a YAML file. See `config/config.yaml` for an example.

```yaml
# Strategy Parameters
strategy:
  ema_pairs:
    - [9, 21]   # Fast EMA, Slow EMA
    - [13, 34]
    - [21, 55]

  trading:
    mode: ["SWING"]  # Options: "BUY", "SELL", "SWING"

  ha_patterns:
    enabled: true
    confirmation_candles: [2, 3, null]  # Number of consecutive candles required for pattern confirmation
                                        # null means no pattern filtering (basic Heikin Ashi only)

  trading_session:
    market_open: "09:15"    # Market opens
    market_entry: "09:30"   # Market entry time (after market open) for new trades
    force_exit: "15:15"     # Force exit all positions & no new entries
    market_close: "15:30"   # Market closes

# Backtest Parameters
backtest:
  initial_capital: 25000
  commission: 0.0
  slippage: 0.0

# Risk Management Parameters
risk_management:
  use_stop_loss: true       # Enable stop loss
  stop_loss_pct: 1.0        # Stop loss percentage
  use_trailing_stop: true   # Enable trailing stop
  trailing_stop_pct: 0.5    # Trailing stop percentage
  max_trades_per_day: 5     # Maximum number of trades per day (planned feature)
  max_risk_per_trade: 2.0   # Maximum risk per trade as percentage of capital (planned feature)

# Data Parameters
data:
  data_folder: "data/market_data"
  results_folder: "data/results"
  timeframe: "1min"

# Logging Parameters
logging:
  level: "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL

# Execution Settings
execution:
  mode: "standard"          # standard, deterministic, sequential, validate, cross-validate
  seed: 42                  # Random seed for reproducibility
```

## Data Format

The strategy expects market data in CSV format with the following columns:

- `date`: Date and time in format YYYY-MM-DD HH:MM:SS
- `open`: Open price
- `high`: High price
- `low`: Low price
- `close`: Close price

## Results

Backtest results are saved in the `data/results` directory (configurable) in two formats:

- JSON file with performance metrics
- CSV file with individual trades

## Performance Metrics

The strategy calculates the following performance metrics:

- Total trades
- Win rate
- Profit factor
- Total profit
- Return percentage
- Maximum drawdown
- Sharpe ratio
- Monthly returns statistics

## Excel Reports

The strategy can generate comprehensive Excel reports with the following sheets:

- Overview: Summary of backtest parameters and overall performance
- EMA Pairs Summary: Performance metrics for each EMA pair
- Best Performers: Top performing configurations
- Trading Modes Comparison: Comparison of BUY, SELL, and SWING modes
- Candle Patterns Comparison: Comparison of different candle pattern configurations
- All Combinations: Results for all combinations of parameters

## Testing

The project includes a comprehensive test suite. To run the tests:

```bash
pytest
```

To run tests with coverage report:

```bash
pytest --cov=. --cov-report=term-missing
```

## Project Structure

```
ema_ha_strategy/
├── config/                # Configuration files
│   └── config.yaml        # Default configuration
│
├── data/                  # Data directory
│   ├── market_data/       # Store your market data files here
│   ├── results/           # Backtest results will be saved here
│   └── reports/           # Excel reports will be saved here
│
├── docs/                  # Documentation
│   ├── api/               # API documentation
│   ├── user_guide/        # User guide
│   └── development/       # Development guide
│
├── logs/                  # Log files
│
├── patterns/              # Pattern recognition (deprecated, for backward compatibility)
│   ├── __init__.py        # Imports from utils.patterns
│   └── ha_patterns.py     # Imports from utils.patterns
│
├── strategies/            # Trading strategies
│   ├── __init__.py
│   └── ema_ha.py          # EMA Heikin Ashi strategy
│
├── tests/                 # Test suite
│   ├── integration/       # Integration tests
│   │   ├── __init__.py
│   │   └── test_integration.py
│   ├── unit/              # Unit tests
│   │   ├── __init__.py
│   │   ├── test_config_validator.py
│   │   ├── test_ema_ha_strategy.py
│   │   └── test_utils.py
│   ├── __init__.py
│   ├── test_config_validator.py
│   ├── test_ema_ha.py
│   ├── test_ema_ha_strategy.py
│   ├── test_excel_report.py
│   ├── test_integration.py
│   ├── test_patterns.py
│   └── test_utils.py
│
├── utils/                 # Utility modules
│   ├── __init__.py        # Common utility functions
│   ├── config_validator.py # Configuration validation
│   ├── excel_report.py    # Excel report generation
│   └── patterns.py        # Pattern recognition (new location)
│
├── backtest.py            # Backtesting module
├── backtest_utils.py      # Backtesting utilities
├── cross_validate.py      # Cross-validation module
├── deterministic_backtest.py # Deterministic backtesting
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker configuration
├── health_check.py        # Health check server
├── LICENSE                # License file
├── logger.py              # Logging configuration
├── main.py                # Main entry point
├── pytest.ini             # PyTest configuration
├── quick_validate.py      # Quick validation module
├── README.md              # Project documentation
├── requirements.txt       # Project dependencies
├── setup.py               # Package setup script
├── utils.py               # Legacy utility functions
├── validate_results.py    # Results validation
└── version.py             # Version information
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

* [Pandas](https://pandas.pydata.org/) - Data analysis library
* [NumPy](https://numpy.org/) - Numerical computing library
* [PyYAML](https://pyyaml.org/) - YAML parser and emitter
* [pytest](https://docs.pytest.org/) - Testing framework
