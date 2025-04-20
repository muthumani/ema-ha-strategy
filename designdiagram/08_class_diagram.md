# EMA Heikin Ashi Strategy - Class Diagram

This diagram illustrates the main classes and their relationships in the EMA Heikin Ashi Strategy system.

## Class Diagram

```mermaid
classDiagram
    class EMAHeikinAshiStrategy {
        -int ema_short
        -int ema_long
        -dict config
        +__init__(ema_short, ema_long, config)
        +backtest(data, initial_capital)
        -generate_signals(data)
        -execute_trades(data, signals, initial_capital)
        -calculate_metrics(trades, initial_capital)
    }
    
    class HeikinAshiPattern {
        -dict config
        +__init__(config)
        +detect_pattern(data, pattern_length)
        -is_bullish_pattern(data, index, length)
        -is_bearish_pattern(data, index, length)
    }
    
    class ConfigValidator {
        +validate_config(config)
        -validate_strategy_config(config)
        -validate_backtest_config(config)
        -validate_data_config(config)
    }
    
    class BacktestEngine {
        -dict config
        +__init__(config)
        +run_backtest(strategy, data, initial_capital)
        +run_parallel_backtests(config, data, trading_modes, candle_patterns)
    }
    
    class DeterministicBacktest {
        -int seed
        +__init__(config, seed)
        +run_backtest(strategy, data, initial_capital)
        +run_all_combinations(config, data, trading_modes, candle_patterns, seed)
    }
    
    class ExcelReportGenerator {
        -dict config
        +__init__(config)
        +create_report(results, file_path)
        +create_consolidated_report(all_results, file_path)
        -create_overview_sheet(workbook, results)
        -create_summary_sheet(workbook, results)
        -create_best_performers_sheet(workbook, results)
        -create_comparison_sheet(workbook, results)
    }
    
    class DataLoader {
        +load_data(file_path)
        -validate_data(data)
        -preprocess_data(data)
    }
    
    class ConfigLoader {
        +load_config(config_path)
        -validate_config_file(config_path)
    }
    
    class AcceptanceTester {
        -dict config
        +__init__(config)
        +run_tests(categories)
        +generate_report(results, output_file)
    }
    
    EMAHeikinAshiStrategy --> HeikinAshiPattern : uses
    EMAHeikinAshiStrategy --> BacktestEngine : uses
    BacktestEngine <|-- DeterministicBacktest : extends
    EMAHeikinAshiStrategy --> ExcelReportGenerator : uses
    BacktestEngine --> DataLoader : uses
    EMAHeikinAshiStrategy --> ConfigValidator : uses
    ConfigValidator --> ConfigLoader : uses
    AcceptanceTester --> EMAHeikinAshiStrategy : tests
    AcceptanceTester --> BacktestEngine : tests
    AcceptanceTester --> ExcelReportGenerator : tests
```

## Class Descriptions

### EMAHeikinAshiStrategy
The main strategy class that implements the EMA Heikin Ashi trading strategy.

### HeikinAshiPattern
Detects Heikin Ashi candle patterns for trade signal confirmation.

### ConfigValidator
Validates configuration settings to ensure they meet requirements.

### BacktestEngine
Executes backtests of trading strategies against historical data.

### DeterministicBacktest
A specialized version of the backtest engine that ensures reproducible results.

### ExcelReportGenerator
Generates Excel reports with performance metrics and visualizations.

### DataLoader
Loads and preprocesses market data from CSV files.

### ConfigLoader
Loads configuration settings from YAML files.

### AcceptanceTester
Runs acceptance tests to validate system behavior against requirements.
