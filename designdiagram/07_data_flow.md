# EMA Heikin Ashi Strategy - Data Flow Diagram

This diagram illustrates the data flow within the EMA Heikin Ashi Strategy system.

## Data Flow Diagram

```mermaid
flowchart TB
    subgraph Input ["Input Data"]
        MarketData["Market Data\n(CSV Files)"]
        ConfigData["Configuration\n(YAML Files)"]
        
        MarketData --> |"Load Data"| DataPreprocessing
        ConfigData --> |"Load Config"| ConfigValidation
    end
    
    subgraph Processing ["Data Processing"]
        DataPreprocessing["Data Preprocessing\n- Date parsing\n- Data cleaning\n- Sorting"]
        ConfigValidation["Configuration Validation\n- Schema validation\n- Type checking\n- Default values"]
        
        DataPreprocessing --> |"Processed Data"| IndicatorCalculation
        ConfigValidation --> |"Validated Config"| StrategyParameters
    end
    
    subgraph Analysis ["Technical Analysis"]
        IndicatorCalculation["Indicator Calculation\n- Heikin Ashi candles\n- EMA calculation"]
        StrategyParameters["Strategy Parameters\n- EMA pairs\n- Trading modes\n- Pattern settings"]
        
        IndicatorCalculation --> |"Technical Indicators"| SignalGeneration
        StrategyParameters --> |"Strategy Settings"| SignalGeneration
    end
    
    subgraph Trading ["Trading Logic"]
        SignalGeneration["Signal Generation\n- EMA crossovers\n- Pattern recognition"]
        TradeExecution["Trade Execution\n- Entry/exit logic\n- Position sizing\n- Risk management"]
        
        SignalGeneration --> |"Trading Signals"| TradeExecution
    end
    
    subgraph Results ["Results Processing"]
        TradeCollection["Trade Collection\n- Trade details\n- P&L calculation"]
        PerformanceMetrics["Performance Metrics\n- Win rate\n- Profit factor\n- Sharpe ratio"]
        
        TradeExecution --> |"Trade Data"| TradeCollection
        TradeCollection --> |"Trade Statistics"| PerformanceMetrics
    end
    
    subgraph Output ["Output Generation"]
        ReportGeneration["Report Generation\n- Excel reports\n- CSV exports"]
        Visualization["Visualization\n- Performance charts\n- Equity curves"]
        
        PerformanceMetrics --> |"Performance Data"| ReportGeneration
        PerformanceMetrics --> |"Performance Data"| Visualization
    end
    
    class Input,Processing,Analysis,Trading,Results,Output frame
```

## Data Flow Components

### Input Data
- **Market Data**: Historical price data in CSV format
- **Configuration Data**: System configuration in YAML format

### Data Processing
- **Data Preprocessing**: Prepares market data for analysis
- **Configuration Validation**: Validates configuration settings

### Technical Analysis
- **Indicator Calculation**: Calculates technical indicators
- **Strategy Parameters**: Defines strategy parameters

### Trading Logic
- **Signal Generation**: Generates trading signals
- **Trade Execution**: Executes trades based on signals

### Results Processing
- **Trade Collection**: Collects trade data
- **Performance Metrics**: Calculates performance metrics

### Output Generation
- **Report Generation**: Generates reports
- **Visualization**: Creates visualizations of results
