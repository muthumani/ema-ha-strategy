# Strategies Package

This package contains trading strategy implementations for the EMA Heikin Ashi strategy.

## Modules

### __init__.py

Package initialization.

### ema_ha.py

This module implements the EMA Heikin Ashi strategy.

#### Classes

- `EMAHeikinAshiStrategy`: The main strategy class that implements the EMA Heikin Ashi strategy.

#### Usage

```python
from strategies.ema_ha import EMAHeikinAshiStrategy

# Initialize the strategy
strategy = EMAHeikinAshiStrategy(ema_short=13, ema_long=34, config=config)

# Generate signals
signals_df = strategy.generate_signals(data)

# Run backtest
results, trades = strategy.backtest(data, initial_capital=25000)
```

## Strategy Details

The EMA Heikin Ashi strategy combines Exponential Moving Average (EMA) crossovers with Heikin Ashi candles to identify trading opportunities.

### Signal Generation

The strategy generates signals based on the following conditions:

1. EMA crossover: The fast EMA crosses above/below the slow EMA
2. Heikin Ashi confirmation: The Heikin Ashi candle is bullish/bearish
3. Optional pattern confirmation: A specified number of consecutive Heikin Ashi candles are bullish/bearish

### Trading Modes

The strategy supports the following trading modes:

- `BUY`: Only take long positions
- `SELL`: Only take short positions
- `SWING`: Take both long and short positions

### Risk Management

The strategy implements the following risk management features:

- Stop loss: Exit a position if the price moves against the position by a specified percentage
- Trailing stop: Exit a position if the price retraces from the highest/lowest price by a specified percentage
- Force exit: Exit all positions at a specified time

For more details, see the [API Reference](../docs/api/ema_ha_strategy.md).
