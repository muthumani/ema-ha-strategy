# Patterns Package (Deprecated)

This package contains pattern recognition modules for trading strategies.

## Modules

### ha_patterns.py (Deprecated)

This module has been moved to `utils/patterns.py`. This version is maintained for backward compatibility but imports from the new location.

It's recommended to update your imports to use the new module:

```python
# Old import (deprecated)
from patterns.ha_patterns import apply_ha_pattern_filter

# New import (recommended)
from utils.patterns import apply_ha_pattern_filter
```
