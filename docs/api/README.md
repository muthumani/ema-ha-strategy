# API Reference

This directory contains detailed documentation for the EMA Heikin Ashi Strategy API.

## Core Components

- **[EMAHeikinAshiStrategy](ema_ha_strategy.md)**: The main strategy class
- **[Backtesting](backtesting.md)**: Backtesting functionality
- **[Cross-Validation](cross_validation.md)**: Cross-validation functionality
- **[Utilities](utilities.md)**: Utility functions

## EMAHeikinAshiStrategy

The `EMAHeikinAshiStrategy` class is the main strategy class. It implements the EMA Heikin Ashi strategy.

```python
from strategies.ema_ha import EMAHeikinAshiStrategy

# Initialize the strategy
strategy = EMAHeikinAshiStrategy(ema_short=13, ema_long=34, config=config)

# Generate signals
signals_df = strategy.generate_signals(data)

# Run backtest
results, trades = strategy.backtest(data, initial_capital=25000)
```

For more details, see the [EMAHeikinAshiStrategy documentation](ema_ha_strategy.md).

## Backtesting

The backtesting functionality is implemented in the `backtest.py` and `deterministic_backtest.py` modules.

```python
from deterministic_backtest import DeterministicBacktest

# Run deterministic backtest
results, trades = DeterministicBacktest.run_backtest(
    strategy=strategy,
    data=data,
    config=config,
    seed=42
)
```

For more details, see the [Backtesting documentation](backtesting.md).

## Cross-Validation

The cross-validation functionality is implemented in the `cross_validate.py` module.

```python
from cross_validate import run_parallel_validation

# Run cross-validation
run_parallel_validation(config_path, data_path, seed=42)
```

For more details, see the [Cross-Validation documentation](cross_validation.md).

## Utilities

The utility functions are implemented in the `utils` package.

```python
from backtest_utils import load_config, load_data, save_results
from utils.config_validator import validate_config
from utils.excel_report import create_consolidated_report
from utils.patterns import apply_ha_pattern_filter

# Load configuration
config = load_config('config/config.yaml')

# Validate configuration
if validate_config(config):
    # Load data
    data = load_data('data/market_data/NIFTY_1min.csv')
    
    # Apply pattern filter
    filtered_data = apply_ha_pattern_filter(data, config)
    
    # Create report
    create_consolidated_report(results, trades, config)
```

For more details, see the [Utilities documentation](utilities.md).
