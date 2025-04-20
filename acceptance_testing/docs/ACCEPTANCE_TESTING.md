# EMA-HA Strategy Acceptance Testing Framework

This document describes the acceptance testing framework for the EMA Heikin Ashi Strategy system.

## Overview

The acceptance testing framework is designed to validate that the EMA-HA Strategy system meets all requirements and is ready for production deployment. It includes:

- Automated test scripts
- Test data generation
- Performance monitoring
- Test result documentation
- Production deployment checklist

## Getting Started

### Prerequisites

- Python 3.8+
- All dependencies installed from requirements.txt and requirements-test.txt
- Docker and Docker Compose (optional, for container testing)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```
3. Make the test scripts executable:
   ```bash
   chmod +x acceptance_test.sh
   chmod +x smoke_test.sh
   ```

## Running Acceptance Tests

### Full Acceptance Test Suite

To run the full acceptance test suite:

```bash
./acceptance_test.sh
```

This will run all test categories and generate a comprehensive test report in the `logs` directory.

### Smoke Test

For a quick validation after deployment:

```bash
./smoke_test.sh
```

### Performance Monitoring

To monitor system performance during test execution:

```bash
python monitor_performance.py "python main.py --all"
```

This will generate a performance report with CPU and memory usage graphs.

### Generating Test Data

To generate synthetic market data for testing:

```bash
python generate_test_data.py --days 30 --interval 1 --volatility 0.01
```

## Test Categories

The acceptance test suite includes the following categories:

1. **Unit Tests**: Tests for individual components
2. **Integration Tests**: Tests for component interactions
3. **Functional Tests**: Tests for basic functionality
4. **Comparative Analysis Tests**: Tests for comparative analysis features
5. **Report Generation Tests**: Tests for Excel report generation
6. **Performance Tests**: Tests for system performance
7. **Cross-Validation Tests**: Tests for result consistency
8. **Error Handling Tests**: Tests for error handling
9. **Docker Tests**: Tests for containerized deployment

## Acceptance Criteria

The system is considered ready for production when:

- All acceptance tests pass
- Code coverage is >95% for core modules
- All critical and high-severity issues are resolved
- Performance meets acceptance criteria
- Documentation is complete and up-to-date

## Test Result Documentation

Test results are documented using the following templates:

- `test_result_template.md`: Template for individual test results
- `test_summary_template.md`: Template for the test summary report

## Production Deployment

The production deployment process is guided by the `production_deployment_checklist.md` document, which includes:

- Pre-deployment verification
- Deployment steps
- Post-deployment verification
- Rollback procedure

## Continuous Integration

The acceptance testing framework is integrated with GitHub Actions for continuous integration. The workflow is defined in `.github/workflows/acceptance_ci.yml`.

## Troubleshooting

If you encounter issues during acceptance testing:

1. Check the log files in the `logs` directory
2. Verify that all dependencies are installed
3. Ensure that the test data is available
4. Check the system requirements

## Contributing

When adding new features or making changes to the system, update the acceptance test suite accordingly to maintain test coverage.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
