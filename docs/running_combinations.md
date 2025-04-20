# Running All Trading Mode Combinations

This document explains how to run all trading mode combinations (BUY, SELL, SWING) with different candle patterns using the existing `main.py` script.

## Running All Combinations in Parallel Mode

To run all trading mode combinations (BUY, SELL, SWING) with different candle patterns in parallel mode:

```bash
python main.py --all-combinations --deterministic --report
```

This command will:
- Run all combinations of trading modes (BUY, SELL, SWING)
- Run all combinations of candle patterns (None, 2-candle, 3-candle)
- Run all combinations of EMA pairs (9/21, 9/26, 13/34, 21/55)
- Use deterministic execution mode for reproducibility
- Generate a consolidated Excel report

## Additional Options

You can customize the execution with additional options:

```bash
python main.py --all-combinations --deterministic --report --symbol NIFTY --config config/custom_config.yaml --output data/custom_results
```

### Available Options

- `--config`: Path to configuration file (default: config/config.yaml)
- `--data`: Path to market data file (optional, uses config if not provided)
- `--symbol`: Trading symbol (default: NIFTY)
- `--output`: Output directory for results (optional, uses config if not provided)
- `--deterministic`: Use deterministic execution mode for reproducibility
- `--sequential`: Use sequential execution instead of parallel
- `--seed`: Random seed for reproducibility (default: 42)
- `--report`: Generate consolidated Excel report
- `--cross-validate`: Run cross-validation to verify results

## Cross-Validation

To run cross-validation to verify the results:

```bash
python main.py --all-combinations --deterministic --cross-validate
```

This will run all combinations and perform cross-validation to ensure the results are consistent and reproducible.

## Performance Considerations

- Parallel execution is significantly faster but may use more system resources
- For resource-constrained systems, use the `--sequential` flag
- The `--deterministic` flag ensures reproducible results but may be slightly slower
