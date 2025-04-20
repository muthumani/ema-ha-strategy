# EMA Heikin Ashi Strategy - Component Diagram

This diagram shows the main components of the EMA Heikin Ashi Strategy system and their relationships.

## Component Diagram

```mermaid
flowchart TB
    Main["Main Application\n(main.py)"]
    
    subgraph Core ["Core Components"]
        Strategy["Strategy Module\n(strategies/ema_ha.py)"]
        Pattern["Pattern Recognition\n(patterns/patterns.py)"]
        Backtest["Backtesting Engine\n(backtest/*.py)"]
    end
    
    subgraph Utils ["Utility Components"]
        Config["Configuration Module\n(utils/config_utils.py)"]
        Report["Reporting Module\n(utils/excel_report.py)"]
        Utilities["Utilities\n(utils/*.py)"]
    end
    
    subgraph Testing ["Testing Components"]
        TestFramework["Testing Framework\n(tests/*.py)"]
        AcceptanceTesting["Acceptance Testing\n(acceptance_testing/*.py)"]
    end
    
    Main --> Strategy
    Main --> Config
    Main --> Backtest
    
    Strategy --> Pattern
    Strategy --> Backtest
    
    Config --> Strategy
    Config --> Backtest
    Config --> Report
    
    Backtest --> Report
    Backtest --> Utilities
    
    TestFramework --> Strategy
    TestFramework --> Backtest
    TestFramework --> Config
    
    AcceptanceTesting --> Main
    
    class Core,Utils,Testing frame
```

## Component Descriptions

### Main Application
- **main.py**: Entry point for the application, handles command-line arguments and orchestrates the workflow

### Core Components
- **Strategy Module**: Implements the EMA Heikin Ashi trading strategy
- **Pattern Recognition**: Detects Heikin Ashi candle patterns
- **Backtesting Engine**: Executes the strategy against historical data

### Utility Components
- **Configuration Module**: Manages system configuration
- **Reporting Module**: Generates Excel reports and visualizations
- **Utilities**: Common utility functions used throughout the system

### Testing Components
- **Testing Framework**: Unit and integration tests
- **Acceptance Testing**: End-to-end tests for validating system behavior
