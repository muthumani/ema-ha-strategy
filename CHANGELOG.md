# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-04-17

### Added
- Initial release of the EMA Heikin Ashi Strategy
- Support for multiple EMA pairs (9/21, 13/34, 21/55)
- Support for multiple trading modes (BUY, SELL, SWING)
- Support for Heikin Ashi candle pattern filtering (2-candle, 3-candle, None)
- Risk management features (stop loss, trailing stop)
- Comprehensive performance metrics
- Excel reporting with detailed analysis
- Comparative analysis across trading modes and candle patterns
- Configuration validation
- Type hints for better code quality
- Unit tests and integration tests
- Cross-validation with deterministic and sequential execution modes
- Parallel processing for faster backtesting
- Docker support for containerized deployment
- Health check server for production monitoring

### Changed
- Moved pattern recognition from patterns/ to utils/patterns.py
- Improved error handling and logging
- Enhanced performance with vectorized operations
- Optimized memory usage for large datasets

### Fixed
- Fixed timestamp conversion issues in deterministic backtest
- Fixed monthly returns calculation
- Fixed trade duration calculation
- Fixed profit factor calculation edge cases

## [0.9.0] - 2025-04-10

### Added
- Beta release with core functionality
- Basic EMA crossover strategy
- Heikin Ashi candle filtering
- Simple backtesting engine
- Basic performance metrics
- Command-line interface

### Changed
- Improved backtesting performance
- Enhanced logging

### Fixed
- Fixed various bugs in the backtesting engine
- Fixed configuration loading issues

## [0.1.0] - 2025-03-15

### Added
- Initial project setup
- Basic project structure
- Configuration loading
- Market data loading
