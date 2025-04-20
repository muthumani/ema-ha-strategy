# EMA-HA Strategy Acceptance Testing Module

This module contains all the files and scripts needed for acceptance testing of the EMA Heikin Ashi Strategy system.

## Directory Structure

- **scripts/**: Contains all the scripts for running acceptance tests
  - `acceptance_test.bat`: Windows batch file for running the full acceptance test suite
  - `smoke_test.bat`: Windows batch file for quick validation after deployment
  - `monitor_performance.py`: Python script for monitoring system performance during test execution
  - `generate_test_data.py`: Python script for generating synthetic market data for testing

- **docs/**: Contains all the documentation for acceptance testing
  - `ACCEPTANCE_TESTING.md`: Overview of the acceptance testing framework
  - `PRODUCTION_READINESS.md`: Assessment of the system's readiness for production
  - `TEST_IMPROVEMENT_PLAN.md`: Plan for improving test coverage and quality
  - `test_result_template.md`: Template for documenting individual test results
  - `test_summary_template.md`: Template for the test summary report
  - `production_deployment_checklist.md`: Checklist for production deployment

- **reports/**: Directory for storing test reports and results

## Getting Started

### Running the Full Acceptance Test Suite

```
cd acceptance_testing\scripts
acceptance_test.bat
```

### Running the Smoke Test

```
cd acceptance_testing\scripts
smoke_test.bat
```

### Monitoring Performance

```
cd acceptance_testing\scripts
python monitor_performance.py "python ../../main.py --all"
```

### Generating Test Data

```
cd acceptance_testing\scripts
python generate_test_data.py --days 30 --interval 1 --volatility 0.01
```

## Documentation

For more information about the acceptance testing framework, see the following documents:

- [Acceptance Testing Overview](docs/ACCEPTANCE_TESTING.md)
- [Production Readiness Assessment](docs/PRODUCTION_READINESS.md)
- [Test Improvement Plan](docs/TEST_IMPROVEMENT_PLAN.md)
- [Production Deployment Checklist](docs/production_deployment_checklist.md)

## Test Reports

Test reports are stored in the `reports/` directory. The acceptance test script generates the following reports:

- Test results CSV file
- Test output logs
- Performance reports (when using the performance monitoring script)

## Continuous Integration

The acceptance testing framework is integrated with GitHub Actions for continuous integration. The workflow is defined in `.github/workflows/acceptance_ci.yml`.
