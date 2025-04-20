# Patterns Package

This package contains pattern recognition modules for trading strategies.

## Modules

### patterns.py

This module provides functions to identify various Heikin Ashi candlestick patterns that can be used as confirmation signals in trading strategies.

#### Functions

- `detect_consecutive_candles(df, pattern_type, length)`: Detects consecutive bullish or bearish Heikin Ashi candles.
- `apply_ha_pattern_filter(df, config, candle_pattern)`: Applies Heikin Ashi pattern filters to the DataFrame based on configuration.

#### Usage

```python
from patterns.patterns import apply_ha_pattern_filter

# Apply pattern filter to DataFrame
df = apply_ha_pattern_filter(df, config, candle_pattern=2)
```

