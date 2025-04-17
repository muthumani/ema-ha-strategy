# Utils Package

This package contains utility modules for the EMA Heikin Ashi strategy.

## Modules

### __init__.py

Common utility functions used throughout the project.

### config_validator.py

This module provides functions for validating configuration files against a schema.

#### Functions

- `validate_config(config)`: Validates a configuration dictionary against the schema.
- `validate_config_file(config_path)`: Validates a configuration file against the schema.

#### Usage

```python
from utils.config_validator import validate_config

# Validate configuration
if validate_config(config):
    # Configuration is valid
    pass
else:
    # Configuration is invalid
    pass
```

### excel_report.py

This module provides functions for generating Excel reports with detailed analysis.

#### Functions

- `create_consolidated_report(results, trades, config)`: Creates a consolidated Excel report with multiple sheets.
- `create_excel_report(results, trades, config)`: Creates a basic Excel report.

#### Usage

```python
from utils.excel_report import create_consolidated_report

# Create consolidated report
create_consolidated_report(results, trades, config)
```

### patterns.py

This module provides functions to identify various Heikin Ashi candlestick patterns that can be used as confirmation signals in trading strategies.

The module replaces the functionality previously found in `patterns/ha_patterns.py`. The old module is still available for backward compatibility but imports from this new module.

#### Functions

- `detect_consecutive_candles(df, pattern_type, length)`: Detects consecutive bullish or bearish Heikin Ashi candles.
- `apply_ha_pattern_filter(df, config, candle_pattern)`: Applies Heikin Ashi pattern filters to the DataFrame based on configuration.

#### Usage

```python
from utils.patterns import apply_ha_pattern_filter

# Apply pattern filter to DataFrame
df = apply_ha_pattern_filter(df, config, candle_pattern=2)
```
