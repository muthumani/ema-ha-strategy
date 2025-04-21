# EMA Heikin Ashi Strategy

![GitHub release (latest by date)](https://img.shields.io/github/v/release/muthumani/ema-ha-strategy)
![GitHub](https://img.shields.io/github/license/muthumani/ema-ha-strategy)
![GitHub Workflow Status](https://img.shields.io/github/workflow/status/muthumani/ema-ha-strategy/Python%20Tests)
![Code Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen)

A comprehensive backtesting and trading system for the EMA Heikin Ashi strategy, designed for NIFTY Index 50 options trading.

## Features

- **Multiple Trading Modes**: Support for BUY, SELL, and SWING (both) trading modes
- **Heikin Ashi Pattern Recognition**: Configurable pattern detection with 2-candle, 3-candle, or no pattern options
- **EMA Crossover Strategy**: Implements the EMA Heikin Ashi strategy with configurable EMA pairs
- **Comprehensive Backtesting**: Robust backtesting engine with detailed performance metrics
- **Parallel Processing**: High-performance parallel backtesting with deterministic mode for reproducibility
- **Cross-Validation**: Ensures consistent results between sequential and parallel execution modes
- **Excel Reporting**: Generates detailed Excel reports with performance metrics and visualizations
- **Acceptance Testing**: Comprehensive acceptance testing framework for production validation

## Performance Highlights

- **Best Performing Combination**:
  - EMA Pair: 13/34
  - Trading Mode: SWING
  - Candle Pattern: None
  - Total Trades: 22,327
  - Win Rate: 30.59%
  - Profit Factor: 1.13
  - Total Profit: Rs.127,092.56
  - Return: 508.37%
  - Max Drawdown: 10.75%
  - Sharpe Ratio: 0.64

## Installation

### Using Command Line

```bash
# Clone the repository
git clone https://github.com/muthumani/ema-ha-strategy.git
cd ema-ha-strategy

# Install dependencies
pip install -r requirements.txt
```

### Using Windows Batch File

For Windows users, a setup batch file is provided for easy installation:

1. Clone the repository
2. Navigate to the repository directory
3. Double-click `setup.bat` or run it from the command prompt

The setup script will create a virtual environment, install all dependencies, and set up the necessary directories.

## Quick Start

### Using Command Line

```bash
# Run a single backtest with default settings
python main.py

# Run with specific trading mode
python main.py --mode BUY

# Run with specific candle pattern
python main.py --pattern 2

# Compare all trading modes
python main.py --compare modes

# Run all combinations and generate a report
python main.py --all --report
```

### Using Windows Batch File

For Windows users, a run batch file is provided for easy execution:

1. Ensure you have completed the installation steps
2. Double-click `run.bat` or run it from the command prompt
3. To pass command-line arguments, run from command prompt: `run.bat --mode BUY`

The run script will activate the virtual environment, check for required files, and execute the strategy with the specified arguments.

## Configuration

The system is configured using YAML files. The default configuration file is `config/config.yaml`.

```yaml
# Example configuration
strategy:
  ema_pairs:
    - [9, 21]
    - [13, 34]
    - [21, 55]
  trading:
    mode: ["SWING"]  # Options: "BUY", "SELL", "SWING"
  ha_patterns:
    enabled: true
    confirmation_candles: [2, 3, null]  # Options: 2, 3, null (no pattern)

backtest:
  initial_capital: 25000
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

## Design Diagrams

The project includes comprehensive design diagrams that illustrate the system architecture, components, and workflows. These diagrams are available in the `designdiagram` folder and can be viewed directly on GitHub.

- [System Architecture](designdiagram/01_system_architecture.md)
- [Component Diagram](designdiagram/02_component_diagram.md)
- [System Design](designdiagram/03_system_design.md)
- [Test Architecture](designdiagram/04_test_architecture.md)
- [Acceptance Testing Workflow](designdiagram/05_acceptance_testing_workflow.md)
- [Deployment Architecture](designdiagram/06_deployment_architecture.md)
- [Data Flow Diagram](designdiagram/07_data_flow.md)
- [Class Diagram](designdiagram/08_class_diagram.md)

## Testing

The project includes a comprehensive testing framework with unit tests, integration tests, and acceptance tests.

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests
pytest tests/integration/

# Run acceptance tests
cd acceptance_testing/scripts
python run_acceptance_tests.py --categories all
```

## Project Structure

```
ema_ha_strategy/
├── .github/               # GitHub configuration
│   ├── ISSUE_TEMPLATE/     # Issue templates
│   └── workflows/         # GitHub Actions workflows
│
├── acceptance_testing/    # Acceptance testing framework
│   ├── docs/              # Acceptance testing documentation
│   ├── reports/           # Acceptance test reports
│   ├── scripts/           # Acceptance test scripts
│   │   ├── acceptance_test.bat    # Windows batch file for acceptance tests
│   │   ├── generate_test_data.py  # Generate synthetic test data
│   │   ├── monitor_performance.py # Monitor system performance
│   │   ├── run_acceptance_tests.py # Run acceptance tests
│   │   ├── smoke_test.bat         # Quick smoke test
│   │   └── __init__.py            # Package initialization
│   ├── __init__.py        # Package initialization
│   ├── main.py            # Main entry point for acceptance testing
│   └── README.md          # Acceptance testing documentation
│
├── backtest/              # Backtesting framework
│   ├── cross_validate.py  # Cross-validation implementation
│   ├── deterministic.py   # Deterministic backtesting
│   ├── parallel.py        # Parallel backtesting
│   ├── quick_validate.py  # Quick validation
│   ├── run.py             # Backtest runner
│   ├── runner.py          # Backtest runner implementation
│   ├── utils.py           # Backtesting utilities
│   ├── validate.py        # Validation utilities
│   └── __init__.py        # Package initialization
│
├── config/                # Configuration files
│   └── config.yaml        # Default configuration
│
├── data/                  # Data directory
│   ├── market_data/       # Market data files
│   ├── reports/           # Excel reports
│   ├── results/           # Backtest results
│   ├── test_results/      # Test results
│   └── validation/        # Validation results
│
├── designdiagram/         # Design diagrams
│   ├── 01_system_architecture.md    # System architecture diagram
│   ├── 02_component_diagram.md      # Component diagram
│   ├── 03_system_design.md          # System design diagram
│   ├── 04_test_architecture.md      # Test architecture diagram
│   ├── 05_acceptance_testing_workflow.md  # Acceptance testing workflow
│   ├── 06_deployment_architecture.md # Deployment architecture
│   ├── 07_data_flow.md              # Data flow diagram
│   ├── 08_class_diagram.md          # Class diagram
│   └── README.md                    # Design diagrams documentation
│
├── docs/                  # Documentation
│   ├── api/               # API documentation
│   ├── development/       # Development guide
│   ├── user_guide/        # User guide
│   ├── ACCEPTANCE_TESTING_SUMMARY.md # Acceptance testing summary
│   ├── README.md          # Documentation overview
│   ├── running_combinations.md      # Guide for running combinations
│   └── usage_guide.md     # Usage guide
│
├── logs/                  # Log files
│
├── patterns/              # Pattern recognition
│   ├── patterns.py        # Pattern recognition implementation
│   └── __init__.py        # Package initialization
│
├── server/                # Server components
│   ├── health_check.py    # Health check server
│   └── __init__.py        # Package initialization
│
├── strategies/            # Trading strategies
│   ├── ema_ha.py          # EMA Heikin Ashi strategy
│   └── __init__.py        # Package initialization
│
├── tests/                 # Test suite
│   ├── integration/       # Integration tests
│   ├── unit/              # Unit tests
│   ├── fixtures.py        # Test fixtures
│   ├── test_backtest_utils.py    # Tests for backtest utilities
│   ├── test_config_validator.py  # Tests for config validation
│   ├── test_cross_validate.py    # Tests for cross-validation
│   ├── test_deterministic.py     # Tests for deterministic backtest
│   ├── test_ema_ha.py            # Tests for EMA-HA
│   ├── test_ema_ha_strategy.py   # Tests for EMA-HA strategy
│   ├── test_excel_report.py      # Tests for Excel reports
│   ├── test_integration.py       # Integration tests
│   ├── test_main.py              # Tests for main module
│   ├── test_parallel.py          # Tests for parallel execution
│   ├── test_patterns.py          # Tests for patterns
│   ├── test_patterns_functions.py # Tests for pattern functions
│   ├── test_quick_validate.py    # Tests for quick validation
│   ├── test_run.py               # Tests for run module
│   ├── test_runner.py            # Tests for runner module
│   ├── test_utils.py             # Tests for utilities
│   ├── test_validate.py          # Tests for validation
│   └── __init__.py               # Package initialization
│
├── utils/                 # Utility modules
│   ├── config_utils.py    # Configuration utilities
│   ├── config_validator.py # Configuration validation
│   ├── constants.py       # Constants definition
│   ├── excel_report.py    # Excel report generation
│   ├── logger.py          # Logging configuration
│   ├── version.py         # Version information
│   └── __init__.py        # Package initialization
│
├── main.py                # Main entry point
├── setup.py               # Package setup script
├── version.py             # Version information
├── __init__.py            # Package initialization
├── run.bat                # Windows batch file to run the strategy
├── setup.bat              # Windows batch file to set up the environment
└── README.md              # Project documentation
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request at https://github.com/muthumani/ema-ha-strategy/compare/master?expand=1

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all contributors who have helped with the development of this project
- Special thanks to the open-source community for providing the tools and libraries used in this project
