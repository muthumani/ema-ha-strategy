#!/usr/bin/env python
"""
Run Backtest Script

This script provides a simple entry point for running backtests.
"""

import argparse
from pathlib import Path
from backtest.runner import main as run_backtest

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Run EMA Heikin Ashi Strategy Backtest')
    
    parser.add_argument('--config', type=str, default='config/config.yaml',
                        help='Path to configuration file')
    
    parser.add_argument('--data', type=str,
                        help='Path to market data file (overrides config)')
    
    return parser.parse_args()

def main():
    """Main entry point"""
    args = parse_arguments()
    
    # Run backtest
    run_backtest()
    
    return 0

if __name__ == '__main__':
    main()
