# Configuration Guide

This guide explains how to configure the EMA Heikin Ashi Strategy.

## Configuration File

The strategy is configured using a YAML file. The default configuration file is `config/config.yaml`.

### Example Configuration

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

## Configuration Options

### Strategy Parameters

#### EMA Pairs

The `ema_pairs` parameter specifies the EMA periods to use for the strategy. Each pair consists of a fast EMA period and a slow EMA period.

```yaml
strategy:
  ema_pairs:
    - [9, 21]   # Fast EMA, Slow EMA
    - [13, 34]
    - [21, 55]
```

#### Trading Mode

The `trading.mode` parameter specifies the trading mode to use. The options are:

- `BUY`: Only take long positions
- `SELL`: Only take short positions
- `SWING`: Take both long and short positions

```yaml
strategy:
  trading:
    mode: ["SWING"]  # Options: "BUY", "SELL", "SWING"
```

#### Heikin Ashi Patterns

The `ha_patterns` parameter specifies the Heikin Ashi pattern filtering options.

```yaml
strategy:
  ha_patterns:
    enabled: true
    confirmation_candles: [2, 3, null]  # Number of consecutive candles required for pattern confirmation
                                        # null means no pattern filtering (basic Heikin Ashi only)
```

#### Trading Session

The `trading_session` parameter specifies the trading session times.

```yaml
strategy:
  trading_session:
    market_open: "09:15"    # Market opens
    market_entry: "09:30"   # Market entry time (after market open) for new trades
    force_exit: "15:15"     # Force exit all positions & no new entries
    market_close: "15:30"   # Market closes
```

### Backtest Parameters

The `backtest` parameter specifies the backtesting parameters.

```yaml
backtest:
  initial_capital: 25000
  commission: 0.0
  slippage: 0.0
```

### Risk Management Parameters

The `risk_management` parameter specifies the risk management parameters.

```yaml
risk_management:
  use_stop_loss: true       # Enable stop loss
  stop_loss_pct: 1.0        # Stop loss percentage
  use_trailing_stop: true   # Enable trailing stop
  trailing_stop_pct: 0.5    # Trailing stop percentage
  max_trades_per_day: 5     # Maximum number of trades per day (planned feature)
  max_risk_per_trade: 2.0   # Maximum risk per trade as percentage of capital (planned feature)
```

### Data Parameters

The `data` parameter specifies the data parameters.

```yaml
data:
  data_folder: "data/market_data"
  results_folder: "data/results"
  timeframe: "1min"
```

### Logging Parameters

The `logging` parameter specifies the logging parameters.

```yaml
logging:
  level: "INFO"  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Execution Settings

The `execution` parameter specifies the execution settings.

```yaml
execution:
  mode: "standard"          # standard, deterministic, sequential, validate, cross-validate
  seed: 42                  # Random seed for reproducibility
```

## Command Line Overrides

Many configuration options can be overridden using command line arguments. For example:

```bash
python main.py --mode BUY --candle-pattern 2 --execution-mode deterministic --seed 42
```

For a complete list of command line arguments, see the [Running the Strategy](running.md) guide.
