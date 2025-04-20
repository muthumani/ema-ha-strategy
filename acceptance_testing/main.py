#!/usr/bin/env python
"""
Main entry point for the acceptance testing module.
This script provides a command-line interface for running acceptance tests.
"""

import os
import sys
import argparse
from scripts.run_acceptance_tests import run_tests

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='EMA-HA Strategy Acceptance Testing')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Run tests command
    run_parser = subparsers.add_parser('run', help='Run acceptance tests')
    run_parser.add_argument('--categories', nargs='+', 
                           choices=['unit', 'integration', 'functional', 'comparative', 
                                   'report', 'performance', 'validation', 'error', 'all'],
                           default=['all'], help='Test categories to run')
    run_parser.add_argument('--output', help='Output CSV file for test results')
    run_parser.add_argument('--quick', action='store_true', help='Run only a subset of tests for quick validation')
    
    # Smoke test command
    smoke_parser = subparsers.add_parser('smoke', help='Run smoke test')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Monitor system performance during test execution')
    monitor_parser.add_argument('command', help='Command to execute and monitor')
    monitor_parser.add_argument('--interval', type=float, default=1.0, help='Sampling interval in seconds')
    monitor_parser.add_argument('--output', help='Output report file')
    
    # Generate test data command
    generate_parser = subparsers.add_parser('generate', help='Generate synthetic market data for testing')
    generate_parser.add_argument('--output', default='data/market_data/test_data.csv', help='Output file path')
    generate_parser.add_argument('--days', type=int, default=30, help='Number of days to generate')
    generate_parser.add_argument('--interval', type=int, default=1, help='Interval in minutes')
    generate_parser.add_argument('--volatility', type=float, default=0.01, help='Price volatility')
    generate_parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility')
    
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Change to the project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    os.chdir(project_root)
    
    if args.command == 'run':
        # Run acceptance tests
        output_file = args.output
        if not output_file:
            import datetime
            output_file = f"acceptance_testing/reports/test_results_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return run_tests(args.categories, output_file, args.quick)
    
    elif args.command == 'smoke':
        # Run smoke test
        if sys.platform == 'win32':
            os.system('acceptance_testing\\scripts\\smoke_test.bat')
        else:
            os.system('acceptance_testing/scripts/smoke_test.sh')
        return 0
    
    elif args.command == 'monitor':
        # Monitor system performance
        from scripts.monitor_performance import monitor_performance, generate_report
        
        data = monitor_performance(args.command, args.interval)
        output_file = args.output
        if not output_file:
            import datetime
            output_file = f"acceptance_testing/reports/performance_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        generate_report(data, output_file)
        return 0
    
    elif args.command == 'generate':
        # Generate test data
        from scripts.generate_test_data import generate_market_data
        
        df = generate_market_data(
            days=args.days,
            interval=args.interval,
            volatility=args.volatility,
            seed=args.seed
        )
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(args.output), exist_ok=True)
        
        # Save to CSV
        df.to_csv(args.output, index=False)
        
        print(f"Generated {len(df)} candles")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"Data saved to: {args.output}")
        
        return 0
    
    else:
        print("No command specified. Use --help for usage information.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
