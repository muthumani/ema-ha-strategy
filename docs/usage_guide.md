# EMA-HA Strategy Usage Guide

This guide explains how to use the EMA-HA Strategy backtester with the simplified command-line interface.

## Basic Usage

### Run a Single Backtest

To run a single backtest with default settings:

```bash
python main.py
```

This will use the settings from `config/config.yaml`.

### Specify Trading Mode

To run with a specific trading mode:

```bash
python main.py --mode BUY
```

Available modes: `BUY`, `SELL`, `SWING`

### Specify Candle Pattern

To run with a specific candle pattern:

```bash
python main.py --pattern 2
```

Available patterns: `2`, `3`, `None`

## Comparative Analysis

### Compare Trading Modes

To compare all trading modes (BUY, SELL, SWING):

```bash
python main.py --compare modes
```

### Compare Candle Patterns

To compare all candle patterns (2-candle, 3-candle):

```bash
python main.py --compare patterns
```

## Run All Combinations

To run all combinations of trading modes and candle patterns:

```bash
python main.py --all
```

To also generate a consolidated Excel report:

```bash
python main.py --all --report
```

## Advanced Options

### Deterministic Execution

For reproducible results:

```bash
python main.py --deterministic
```

### Sequential Execution

For more stable execution (slower but more reliable):

```bash
python main.py --sequential
```

### Cross-Validation

To validate results:

```bash
python main.py --validate
```

### Quick Validation

To run a quick validation before execution:

```bash
python main.py --quick-validate
```

## Configuration Options

### Custom Configuration File

```bash
python main.py --config path/to/custom_config.yaml
```

### Custom Data File

```bash
python main.py --data path/to/market_data.csv
```

### Custom Symbol

```bash
python main.py --symbol BANKNIFTY
```

### Custom Output Directory

```bash
python main.py --output path/to/results
```

## Common Use Cases

### Backtest with Specific Settings

```bash
python main.py --mode BUY --pattern 2
```

### Compare Modes with a Specific Pattern

```bash
python main.py --compare modes --pattern 2
```

### Run All Combinations with Report

```bash
python main.py --all --report --deterministic
```

### Cross-Validate Results

```bash
python main.py --all --validate
```
