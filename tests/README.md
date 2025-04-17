# Tests

This directory contains the test suite for the EMA Heikin Ashi Strategy.

## Test Structure

The tests are organized into the following directories:

- **integration/**: Integration tests that test the interaction between components
- **unit/**: Unit tests that test individual components
- **Root level**: Legacy tests and tests that don't fit into the above categories

## Running Tests

To run all tests:

```bash
pytest
```

To run tests with coverage report:

```bash
pytest --cov=. --cov-report=term-missing
```

To run a specific test file:

```bash
pytest tests/test_ema_ha.py
```

To run a specific test function:

```bash
pytest tests/test_ema_ha.py::test_calculate_ema
```

## Test Files

### Integration Tests

- **test_integration.py**: Tests the end-to-end workflow of the strategy

### Unit Tests

- **test_config_validator.py**: Tests the configuration validation
- **test_ema_ha_strategy.py**: Tests the EMA Heikin Ashi strategy
- **test_utils.py**: Tests the utility functions

### Root Level Tests

- **test_config_validator.py**: Tests the configuration validation
- **test_ema_ha.py**: Tests the EMA Heikin Ashi strategy
- **test_ema_ha_strategy.py**: Tests the EMA Heikin Ashi strategy
- **test_excel_report.py**: Tests the Excel report generation
- **test_integration.py**: Tests the end-to-end workflow of the strategy
- **test_patterns.py**: Tests the pattern recognition
- **test_utils.py**: Tests the utility functions

## Writing Tests

When writing tests, follow these guidelines:

1. Use descriptive test names that clearly indicate what is being tested
2. Use pytest fixtures for setup and teardown
3. Use assertions to verify expected behavior
4. Use mocks and stubs to isolate the component being tested
5. Use parameterized tests to test multiple scenarios

For more details, see the [Testing Guide](../docs/development/testing.md).
