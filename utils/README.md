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

### patterns.py (Deprecated)

This module is maintained for backward compatibility and imports from `patterns.patterns`.

The functionality has been moved to `patterns/patterns.py`. It's recommended to update your imports to use the new module:

```python
# Old import (deprecated)
from utils.patterns import apply_ha_pattern_filter

# New import (recommended)
from patterns.patterns import apply_ha_pattern_filter
```
