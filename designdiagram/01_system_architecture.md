# EMA Heikin Ashi Strategy - System Architecture

This diagram provides a high-level overview of the EMA Heikin Ashi Strategy system architecture.

## System Architecture Diagram

```mermaid
flowchart TB
    subgraph External ["External Systems"]
        MarketData["Market Data Source"]
    end

    subgraph Core ["EMA-HA Strategy System"]
        Config["Configuration Management"]
        Backtest["Backtesting Engine"]
        Strategy["Strategy Implementation"]
        Analysis["Performance Analysis"]
        
        Config --> Backtest
        Config --> Strategy
        Strategy --> Backtest
        Backtest --> Analysis
    end

    subgraph Output ["Output Systems"]
        Reports["Results & Reports Generation"]
    end

    subgraph Testing ["Testing Framework"]
        UnitTests["Unit Tests"]
        IntegrationTests["Integration Tests"]
        AcceptanceTests["Acceptance Tests"]
    end

    MarketData --> Core
    Core --> Reports
    Core --> Testing
    Testing --> Core

    class External,Core,Output,Testing frame
```

## Components Description

### External Systems
- **Market Data Source**: Provides historical price data for backtesting

### EMA-HA Strategy System
- **Configuration Management**: Handles system configuration via YAML files
- **Strategy Implementation**: Implements the EMA Heikin Ashi trading strategy
- **Backtesting Engine**: Executes the strategy against historical data
- **Performance Analysis**: Calculates performance metrics and statistics

### Output Systems
- **Results & Reports Generation**: Creates Excel reports and visualizations

### Testing Framework
- **Unit Tests**: Tests individual components
- **Integration Tests**: Tests component interactions
- **Acceptance Tests**: Validates system behavior against requirements
