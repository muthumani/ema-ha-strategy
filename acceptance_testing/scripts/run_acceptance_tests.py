#!/usr/bin/env python
"""
Python script for running acceptance tests for the EMA Heikin Ashi Strategy system.
This script provides a programmatic way to run the acceptance tests.
"""

import os
import sys
import argparse
import subprocess
import datetime
import csv
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"../reports/acceptance_test_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger(__name__)

# Define test categories
TEST_CATEGORIES = {
    'unit': [
        ('UT-001', 'Run all unit tests', 'pytest tests/unit/ -v'),
        ('UT-002', 'Run unit tests with coverage', 'pytest tests/unit/ --cov=. --cov-report=term-missing'),
    ],
    'integration': [
        ('IT-001', 'Run all integration tests', 'pytest tests/integration/ -v'),
        ('IT-002', 'Run integration tests with coverage', 'pytest tests/integration/ --cov=. --cov-report=term-missing'),
    ],
    'functional': [
        ('F-001', 'Run single backtest with default settings', 'python main.py'),
        ('F-002', 'Run with specific trading mode (BUY)', 'python main.py --mode BUY'),
        ('F-003', 'Run with specific trading mode (SELL)', 'python main.py --mode SELL'),
        ('F-004', 'Run with specific trading mode (SWING)', 'python main.py --mode SWING'),
        ('F-005', 'Run with specific candle pattern (2)', 'python main.py --pattern 2'),
        ('F-006', 'Run with specific candle pattern (3)', 'python main.py --pattern 3'),
        ('F-007', 'Run with specific candle pattern (None)', 'python main.py --pattern None'),
    ],
    'comparative': [
        ('C-001', 'Compare all trading modes', 'python main.py --compare modes'),
        ('C-002', 'Compare all candle patterns', 'python main.py --compare patterns'),
        ('C-003', 'Run all combinations', 'python main.py --all'),
    ],
    'report': [
        ('R-001', 'Generate Excel report', 'python main.py --report'),
        ('R-002', 'Generate consolidated report', 'python main.py --all --report'),
    ],
    'performance': [
        ('P-001', 'Run single backtest performance', 'python main.py'),
        ('P-002', 'Run all combinations performance', 'python main.py --all'),
    ],
    'validation': [
        ('V-001', 'Run cross-validation', 'python main.py --validate'),
        ('V-002', 'Run deterministic mode', 'python main.py --deterministic --seed 42'),
        ('V-003', 'Run sequential mode', 'python main.py --sequential'),
    ],
    'error': [
        ('E-001', 'Invalid configuration file', 'python main.py --config nonexistent.yaml', 0),
        ('E-002', 'Missing market data', 'python main.py --data nonexistent.csv', 1),
        ('E-003', 'Invalid command line arguments', 'python main.py --invalid-argument', 2),
    ],
}

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run acceptance tests for EMA-HA Strategy')
    parser.add_argument('--categories', nargs='+', choices=list(TEST_CATEGORIES.keys()) + ['all'],
                        default=['all'], help='Test categories to run')
    parser.add_argument('--output', default=f"../reports/test_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        help='Output CSV file for test results')
    parser.add_argument('--quick', action='store_true', help='Run only a subset of tests for quick validation')
    return parser.parse_args()

def run_test(test_id, description, command, expected_exit_code=0):
    """Run a single test and return the result"""
    logger.info(f"Running Test {test_id}: {description}")
    logger.info(f"Command: {command}")

    # Measure execution time
    start_time = datetime.datetime.now()

    # Run the command and capture output
    output_file = f"../reports/{test_id}_output.log"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    try:
        with open(output_file, 'w') as f:
            process = subprocess.run(command, shell=True, stdout=f, stderr=subprocess.STDOUT)
        exit_code = process.returncode
    except Exception as e:
        logger.error(f"Error running test: {e}")
        exit_code = -1

    # Calculate duration
    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Check if test passed
    if exit_code == expected_exit_code:
        status = "PASS"
        logger.info(f"[PASS] Test {test_id} passed ({duration:.2f}s)")
    else:
        status = "FAIL"
        logger.error(f"[FAIL] Test {test_id} failed ({duration:.2f}s)")
        logger.error(f"  Expected exit code: {expected_exit_code}, Actual: {exit_code}")

    # Return result
    return {
        'test_id': test_id,
        'description': description,
        'status': status,
        'duration': duration,
        'exit_code': exit_code,
        'expected_exit_code': expected_exit_code,
    }

def run_tests(categories, output_file, quick=False):
    """Run tests for the specified categories and write results to CSV"""
    # Determine which tests to run
    tests_to_run = []
    if 'all' in categories:
        for category in TEST_CATEGORIES:
            tests_to_run.extend(TEST_CATEGORIES[category])
    else:
        for category in categories:
            tests_to_run.extend(TEST_CATEGORIES[category])

    # If quick mode, run only a subset of tests
    if quick:
        quick_tests = [
            ('UT-001', 'Run all unit tests', 'pytest tests/unit/ -v'),
            ('F-001', 'Run single backtest with default settings', 'python main.py'),
            ('V-001', 'Run cross-validation', 'python main.py --validate'),
        ]
        tests_to_run = [test for test in tests_to_run if test[0] in [qt[0] for qt in quick_tests]]

    # Run tests and collect results
    results = []
    for test in tests_to_run:
        if len(test) == 3:
            test_id, description, command = test
            expected_exit_code = 0
        else:
            test_id, description, command, expected_exit_code = test

        result = run_test(test_id, description, command, expected_exit_code)
        results.append(result)

    # Write results to CSV
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['test_id', 'description', 'status', 'duration', 'exit_code', 'expected_exit_code'])
        writer.writeheader()
        writer.writerows(results)

    # Generate summary
    pass_count = sum(1 for result in results if result['status'] == 'PASS')
    total_count = len(results)
    pass_percentage = pass_count * 100 / total_count if total_count > 0 else 0

    logger.info("\n======================================================")
    logger.info("   Acceptance Test Summary")
    logger.info("======================================================")
    logger.info(f"Total Tests: {total_count}")
    logger.info(f"Passed Tests: {pass_count}")
    logger.info(f"Failed Tests: {total_count - pass_count}")
    logger.info(f"Pass Percentage: {pass_percentage:.2f}%")

    if pass_percentage >= 95:
        logger.info(f"ACCEPTANCE CRITERIA MET: {pass_percentage:.2f}% of tests passed")
        return 0
    else:
        logger.error(f"ACCEPTANCE CRITERIA NOT MET: Only {pass_percentage:.2f}% of tests passed (95% required)")
        return 1

def main():
    """Main entry point"""
    args = parse_arguments()

    logger.info("======================================================")
    logger.info("   EMA-HA Strategy Acceptance Testing Suite")
    logger.info(f"   {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("======================================================")

    # Change to the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
    os.chdir(project_root)

    # Run tests
    return run_tests(args.categories, args.output, args.quick)

if __name__ == "__main__":
    sys.exit(main())
