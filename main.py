#!/usr/bin/env python
"""
EMA Heikin Ashi Strategy - Main Entry Point
This script serves as the main entry point for running the EMA Heikin Ashi strategy.

Version: 1.0.0
"""

import argparse
import sys
import os
import multiprocessing
from pathlib import Path
import logging
from typing import Dict, Any, List, Tuple, Optional, Union

from strategies.ema_ha import EMAHeikinAshiStrategy
from backtest.utils import load_data, save_results
from utils.config_validator import validate_config
from utils.logger import setup_logger
from utils.excel_report import create_consolidated_report
from backtest.parallel import run_parallel_backtests
from backtest.deterministic import DeterministicBacktest
from utils.version import __version__
from server.health_check import start_health_check_server
from utils import constants
from utils.config_utils import get_config, get_config_value, get_symbol, get_trading_modes, get_candle_patterns, get_execution_settings

# Set up logger
logger = setup_logger(name="main", log_level=logging.INFO)

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='EMA Heikin Ashi Strategy Backtester',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Example usage:
  # Run a single backtest with default settings
  python main.py

  # Run with specific trading mode
  python main.py --mode BUY

  # Compare all trading modes
  python main.py --compare modes

  # Compare all candle patterns
  python main.py --compare patterns

  # Run all combinations and generate a report
  python main.py --all --report

  # Run with deterministic mode for reproducibility
  python main.py --deterministic

  # Run cross-validation
  python main.py --validate
''')

    # Create argument groups for better organization
    basic_group = parser.add_argument_group('Basic Options')
    strategy_group = parser.add_argument_group('Strategy Options')
    analysis_group = parser.add_argument_group('Analysis Options')
    advanced_group = parser.add_argument_group('Advanced Options')

    # Basic configuration options
    basic_group.add_argument('--config', type=str, default=constants.DEFAULT_CONFIG_PATH,
                        help=f'Path to configuration file (default: {constants.DEFAULT_CONFIG_PATH})')
    basic_group.add_argument('--data', type=str,
                        help='Path to market data file (overrides config)')
    basic_group.add_argument('--symbol', type=str, default=constants.DEFAULT_SYMBOL,
                        help=f'Trading symbol (default: {constants.DEFAULT_SYMBOL})')
    basic_group.add_argument('--output', type=str,
                        help='Output directory for results (overrides config)')
    basic_group.add_argument('--debug', action='store_true',
                        help='Enable debug logging')

    # Strategy options
    strategy_group.add_argument('--mode', type=str, choices=['BUY', 'SELL', 'SWING'],
                        help='Trading mode: BUY, SELL, or SWING (overrides config)')
    strategy_group.add_argument('--pattern', type=str, choices=['2', '3', 'None'], dest='candle_pattern',
                        help='Candle pattern: 2, 3, or None (overrides config)')

    # Analysis options
    analysis_group.add_argument('--compare', type=str, choices=['modes', 'patterns'],
                        help='Run comparative analysis (modes or patterns)')
    analysis_group.add_argument('--all', action='store_true', dest='all_combinations',
                        help='Run all combinations of modes and patterns')
    analysis_group.add_argument('--report', action='store_true',
                        help='Generate consolidated Excel report')

    # Execution options
    execution_group = advanced_group.add_mutually_exclusive_group()
    execution_group.add_argument('--deterministic', action='store_true',
                        help='Use deterministic execution for reproducibility')
    execution_group.add_argument('--sequential', action='store_true',
                        help='Use sequential execution (slower but more stable)')

    # Validation options
    validation_group = advanced_group.add_mutually_exclusive_group()
    validation_group.add_argument('--validate', action='store_true', dest='cross_validate',
                        help='Run cross-validation to verify results')
    validation_group.add_argument('--quick-validate', action='store_true',
                        help='Run quick validation before execution')

    advanced_group.add_argument('--seed', type=int, default=42,
                        help='Random seed for reproducibility (default: 42)')

    # Hidden options for backward compatibility
    parser.add_argument('--no-config', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--compare-patterns', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--compare-modes', action='store_true', dest='compare', help=argparse.SUPPRESS)
    parser.add_argument('--execution-mode', type=str, help=argparse.SUPPRESS)

    return parser.parse_args()

def run_strategy(config_path: Union[str, Path], data_path: Optional[Union[str, Path]]=None,
               symbol: str='NIFTY', output_dir: Optional[Union[str, Path]]=None,
               mode: Optional[str]=None, candle_pattern: Optional[int]=None) -> Tuple[List[Dict[str, Any]], List[List[Dict[str, Any]]]]:
    """
    Run the EMA Heikin Ashi strategy with the given configuration

    Args:
        config_path: Path to configuration file
        data_path: Path to market data file (overrides config)
        symbol: Trading symbol
        output_dir: Output directory for results (overrides config)
        mode: Trading mode (BUY, SELL, SWING) to override config
        candle_pattern: Number of consecutive candles required for pattern confirmation (2 or 3)
        compare: Whether to run comparative analysis across all modes
    """
    try:
        # Load configuration
        config = get_config(config_path)

        # Validate configuration
        if not validate_config(config):
            logger.error("Configuration validation failed. Please check your configuration file.")
            raise ValueError("Invalid configuration")

        # Set up logging level from config
        log_level = getattr(logging, config.get('logging', {}).get('level', 'INFO'))
        logger.setLevel(log_level)

        # Override trading mode if specified
        if mode:
            if 'strategy' not in config:
                config['strategy'] = {}
            if 'trading' not in config['strategy']:
                config['strategy']['trading'] = {}
            config['strategy']['trading']['mode'] = [mode]

        # Override candle pattern if specified
        if candle_pattern is not None:  # Check for None explicitly
            if 'strategy' not in config:
                config['strategy'] = {}
            if 'ha_patterns' not in config['strategy']:
                config['strategy']['ha_patterns'] = {'enabled': True}
            config['strategy']['ha_patterns']['enabled'] = True

            # Handle string values from command line
            if candle_pattern == 'None':
                config['strategy']['ha_patterns']['confirmation_candles'] = [None]
            else:
                # Convert string to int
                config['strategy']['ha_patterns']['confirmation_candles'] = [int(candle_pattern)]

        # Determine data path
        if not data_path:
            data_folder = config['data']['data_folder']
            data_path = Path(data_folder) / f"{symbol}_{config['data']['timeframe']}.csv"

        # Load market data
        data = load_data(data_path)

        # Run backtest for each EMA pair
        all_results = []
        all_trades = []

        for ema_short, ema_long in config['strategy']['ema_pairs']:
            logger.info(f"Running backtest for EMA {ema_short}/{ema_long}")

            # Initialize strategy
            strategy = EMAHeikinAshiStrategy(ema_short, ema_long, config)

            # Run backtest
            results, trades = strategy.backtest(data, initial_capital=config['backtest']['initial_capital'])

            # Save results
            if output_dir:
                results_dir = Path(output_dir)
            else:
                results_dir = Path(config['data']['results_folder'])

            results_dir.mkdir(parents=True, exist_ok=True)

            save_results(results, trades, symbol, ema_short, ema_long, data.attrs)

            all_results.append(results)
            all_trades.append(trades)


        # Print summary table of all EMA pairs
        if all_results:
            print("\nSUMMARY OF ALL EMA PAIRS")
            print("=" * 100)
            print(f"{'EMA Pair':<10} {'Mode':<6} {'Trades':<8} {'Win Rate':<10} {'Profit Factor':<15} {'Total Profit':<15} {'Return %':<10} {'Max DD %':<10} {'Sharpe':<8}")
            print("-" * 100)

            # Sort by return percentage
            sorted_results = sorted(all_results, key=lambda x: x.get('return_pct', 0), reverse=True)

            for result in sorted_results:
                # Get trading mode from result
                mode = result.get('trading_mode', 'SWING')

                print(f"{result['ema_short']}/{result['ema_long']:<6} "
                      f"{mode:<6} "
                      f"{result['total_trades']:<8} "
                      f"{result['win_rate']*100:<8.1f}% "
                      f"{result['profit_factor']:<15.2f} "
                      f"Rs.{result['total_profit']:,.0f} "
                      f"{result['return_pct']:<10.1f} "
                      f"{result['max_drawdown_pct']:<10.1f} "
                      f"{result.get('sharpe_ratio', 0):<8.2f}")

            # Find best performing pair by Sharpe ratio
            best_result = max(all_results, key=lambda x: x.get('sharpe_ratio', 0) if x.get('sharpe_ratio', 0) != float('inf') else 0)

            print("\nBEST PERFORMING EMA PAIR (by Sharpe Ratio)")
            print("=" * 50)
            print(f"EMA Pair: {best_result['ema_short']}/{best_result['ema_long']}")
            print(f"Trading Mode: {best_result.get('trading_mode', 'SWING')}")
            print(f"Total Trades: {best_result['total_trades']}")
            print(f"Win Rate: {best_result['win_rate']*100:.1f}%")
            print(f"Profit Factor: {best_result['profit_factor']:.2f}")
            print(f"Total Profit: Rs.{best_result['total_profit']:,.0f}")
            print(f"Return: {best_result['return_pct']:.1f}%")
            print(f"Max Drawdown: {best_result['max_drawdown_pct']:.1f}%")
            print(f"Sharpe Ratio: {best_result.get('sharpe_ratio', 0):.2f}")

            # Print exit reasons
            if 'exit_reasons' in best_result:
                print("\nExit Reasons:")
                for reason, count in best_result['exit_reasons'].items():
                    percentage = count / best_result['total_trades'] * 100
                    print(f"{reason}: {count} trades ({percentage:.1f}%)")



        return all_results, all_trades

    except Exception as e:
        logger.error(f"Error running strategy: {e}")

        raise

def run_all_combinations_analysis(config_path: Union[str, Path],
                              data_path: Optional[Union[str, Path]]=None,
                              symbol: str='NIFTY',
                              deterministic: bool=False,
                              sequential: bool=False,
                              seed: int=42,
                              cross_validate: bool=False) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Run analysis for all combinations of trading modes and candle patterns

    Args:
        config_path: Path to configuration file
        data_path: Path to market data file (overrides config)
        symbol: Trading symbol
        output_dir: Output directory for results (overrides config)
        deterministic: Whether to use deterministic backtesting
        sequential: Whether to force sequential execution
        seed: Random seed for reproducibility
        cross_validate: Whether to run cross-validation
    """
    try:
        # Get trading modes and candle patterns from config
        trading_modes = get_trading_modes()
        candle_patterns = [str(p) if isinstance(p, int) else p for p in get_candle_patterns()]  # Convert integers to strings

        # Load configuration once
        config = get_config(config_path)

        # Load data once
        if not data_path:
            data_folder = config['data']['data_folder']
            data_path = Path(data_folder) / f"{symbol}_{config['data']['timeframe']}.csv"
        data = load_data(data_path)

        # Calculate total number of combinations
        total_combinations = len(trading_modes) * len(candle_patterns) * len(config['strategy']['ema_pairs'])

        # Determine processing mode based on arguments
        processing_mode = "deterministic" if deterministic else "standard"
        execution_mode = "sequential" if sequential else "parallel"

        print(f"\nRunning all combinations: {total_combinations} total tests using {processing_mode} {execution_mode} processing")
        print("=" * 100)

        # Run cross-validation if requested
        if cross_validate:
            logger.info("Running cross-validation to verify results...")
            from backtest.cross_validate import run_parallel_validation
            run_parallel_validation(config_path, data_path, seed)

        # Determine if we should use parallel processing
        use_parallel = not sequential

        if use_parallel:
            # Determine number of workers (use 75% of available cores to avoid overloading the system)
            max_workers = max(1, int(multiprocessing.cpu_count() * 0.75))
            logger.info(f"Using {max_workers} worker processes for parallel backtesting")

            # Run backtests in parallel
            all_combination_results = run_parallel_backtests(
                config=config,
                data=data,
                trading_modes=trading_modes,
                candle_patterns=candle_patterns,
                max_workers=max_workers,
                seed=seed  # Use provided seed for reproducibility
            )
        else:
            # Run backtests sequentially using the deterministic backtest implementation
            logger.info("Using sequential deterministic backtesting")
            all_combination_results = DeterministicBacktest.run_all_combinations(
                config=config,
                data=data,
                trading_modes=trading_modes,
                candle_patterns=candle_patterns,
                seed=seed  # Use provided seed for reproducibility
            )

        # Create empty trades list (we don't collect trades to save memory)
        all_combination_trades = []

        # Print summary table
        print("\nSUMMARY OF ALL COMBINATIONS")
        print("=" * 120)
        print(f"{'EMA Pair':<10} {'Mode':<6} {'Pattern':<8} {'Trades':<8} {'Win Rate':<10} {'Profit Factor':<15} {'Total Profit':<15} {'Return %':<10} {'Max DD %':<10} {'Sharpe':<8}")
        print("-" * 120)

        # Sort by return percentage
        sorted_results = sorted(all_combination_results, key=lambda x: x.get('return_pct', 0), reverse=True)

        # Filter out results that don't have the required keys
        valid_results = []
        for result in sorted_results:
            if all(key in result for key in ['ema_short', 'ema_long', 'trading_mode', 'pattern_length', 'total_trades', 'win_rate', 'profit_factor', 'total_profit', 'return_pct', 'max_drawdown_pct']):
                valid_results.append(result)
            else:
                # Log the missing keys for debugging
                missing_keys = [key for key in ['ema_short', 'ema_long', 'trading_mode', 'pattern_length', 'total_trades', 'win_rate', 'profit_factor', 'total_profit', 'return_pct', 'max_drawdown_pct'] if key not in result]
                logger.warning(f"Skipping result with missing keys: {missing_keys}. Result: {result}")

        for result in valid_results:
            try:
                print(f"{result['ema_short']}/{result['ema_long']:<6} "
                      f"{result['trading_mode']:<6} "
                      f"{result['pattern_length']:<8} "
                      f"{result['total_trades']:<8} "
                      f"{result['win_rate']*100:<8.1f}% "
                      f"{result['profit_factor']:<15.2f} "
                      f"Rs.{result['total_profit']:,.0f} "
                      f"{result['return_pct']:<10.1f} "
                      f"{result['max_drawdown_pct']:<10.1f} "
                      f"{result.get('sharpe_ratio', 0):<8.2f}")
            except Exception as e:
                logger.warning(f"Error printing result: {e}. Result: {result}")

        # Find best performing combination from valid results
        if valid_results:
            try:
                best_result = max(valid_results, key=lambda x: x.get('sharpe_ratio', 0) if x.get('sharpe_ratio', 0) != float('inf') else 0)

                print("\nBEST PERFORMING COMBINATION (by Sharpe Ratio)")
                print("=" * 60)
                print(f"EMA Pair: {best_result['ema_short']}/{best_result['ema_long']}")
                print(f"Trading Mode: {best_result['trading_mode']}")
                pattern = best_result['pattern_length']
                if pattern == 'None':
                    print(f"Candle Pattern: No Pattern")
                else:
                    print(f"Candle Pattern: {pattern}-candle")
                print(f"Total Trades: {best_result['total_trades']}")
                print(f"Win Rate: {best_result['win_rate']*100:.1f}%")
                print(f"Profit Factor: {best_result['profit_factor']:.2f}")
                print(f"Total Profit: Rs.{best_result['total_profit']:,.0f}")
                print(f"Return: {best_result['return_pct']:.1f}%")
                print(f"Max Drawdown: {best_result['max_drawdown_pct']:.1f}%")
                print(f"Sharpe Ratio: {best_result.get('sharpe_ratio', 0):.2f}")
            except Exception as e:
                logger.error(f"Error finding best performing combination: {e}")
        else:
            logger.warning("No valid results found to determine best performing combination")

        return all_combination_results, all_combination_trades

    except Exception as e:
        logger.error(f"Error in all combinations analysis: {e}")
        raise

def run_comparative_patterns_analysis(config_path: Union[str, Path],
                                  data_path: Optional[Union[str, Path]]=None,
                                  symbol: str='NIFTY',
                                  output_dir: Optional[Union[str, Path]]=None,
                                  mode: Optional[str]=None) -> Tuple[Dict[int, List[Dict[str, Any]]], Dict[int, List[Dict[str, Any]]]]:
    """
    Run comparative analysis across all candle patterns

    Args:
        config_path: Path to configuration file
        data_path: Path to market data file (overrides config)
        symbol: Trading symbol
        output_dir: Output directory for results (overrides config)
        mode: Trading mode to use for all pattern tests
    """
    try:
        # Define patterns to compare
        patterns = [2, 3]

        # Store results for each pattern
        all_pattern_results = {}
        all_pattern_trades = {}

        # Run backtest for each pattern
        for pattern in patterns:
            print(f"\n{'='*50}")
            print(f"Running backtest with {pattern}-candle pattern")
            print(f"{'='*50}")

            # Run strategy with this pattern
            results, trades = run_strategy(
                config_path=config_path,
                data_path=data_path,
                symbol=symbol,
                output_dir=output_dir,
                mode=mode,
                candle_pattern=pattern
            )

            # Store results
            all_pattern_results[pattern] = results
            all_pattern_trades[pattern] = trades

        # Print comparison table
        print("\nCOMPARATIVE ANALYSIS OF CANDLE PATTERNS")
        print("=" * 100)

        # Print header
        print(f"{'EMA Pair':<10} {'Metric':<15} {'2-Candle':<15} {'3-Candle':<15}")
        print("-" * 100)

        # Get all unique EMA pairs
        all_ema_pairs = set()
        for pattern_results in all_pattern_results.values():
            for result in pattern_results:
                all_ema_pairs.add(f"{result['ema_short']}/{result['ema_long']}")

        # Sort EMA pairs
        sorted_ema_pairs = sorted(all_ema_pairs)

        # Define metrics to compare
        metrics = ["return_pct", "sharpe_ratio", "win_rate", "profit_factor", "max_drawdown_pct"]

        # Print comparison for each EMA pair and metric
        for ema_pair in sorted_ema_pairs:
            for metric in metrics:
                row = f"{ema_pair:<10} {metric.replace('_', ' ').title():<15}"

                for pattern in patterns:
                    # Find the result for this EMA pair
                    pair_result = next((r for r in all_pattern_results[pattern] if f"{r['ema_short']}/{r['ema_long']}" == ema_pair), None)

                    if pair_result and metric in pair_result:
                        value = pair_result[metric]

                        # Format based on metric type
                        if metric in ['win_rate']:
                            formatted_value = f"{value*100:.1f}%"
                        elif metric in ['return_pct', 'max_drawdown_pct']:
                            formatted_value = f"{value:.1f}%"
                        elif metric in ['profit_factor']:
                            formatted_value = f"{value:.2f}"
                        else:
                            formatted_value = f"{value:.2f}"

                        row += f"{formatted_value:<15}"
                    else:
                        row += f"{'N/A':<15}"

                print(row)

            # Add separator between EMA pairs
            print("-" * 100)

        return all_pattern_results, all_pattern_trades

    except Exception as e:
        logger.error(f"Error in comparative pattern analysis: {e}")
        raise

def run_comparative_analysis(config_path: Union[str, Path],
                           data_path: Optional[Union[str, Path]]=None,
                           symbol: str='NIFTY',
                           output_dir: Optional[Union[str, Path]]=None) -> Tuple[Dict[str, List[Dict[str, Any]]], Dict[str, List[Dict[str, Any]]]]:
    """
    Run comparative analysis across all trading modes

    Args:
        config_path: Path to configuration file
        data_path: Path to market data file (overrides config)
        symbol: Trading symbol
        output_dir: Output directory for results (overrides config)
    """
    try:
        # Define modes to compare
        modes = ['BUY', 'SELL', 'SWING']

        # Store results for each mode
        all_mode_results = {}
        all_mode_trades = {}

        # Run backtest for each mode
        for mode in modes:
            print(f"\n{'='*50}")
            print(f"Running backtest with {mode} mode")
            print(f"{'='*50}")

            # Run strategy with this mode
            results, trades = run_strategy(
                config_path=config_path,
                data_path=data_path,
                symbol=symbol,
                output_dir=output_dir,
                mode=mode,
                candle_pattern=None
            )

            # Store results
            all_mode_results[mode] = results
            all_mode_trades[mode] = trades

        # Print comparison table
        print("\nCOMPARATIVE ANALYSIS OF TRADING MODES")
        print("=" * 100)

        # Print header
        print(f"{'EMA Pair':<10} {'Metric':<15} {'BUY':<15} {'SELL':<15} {'SWING':<15}")
        print("-" * 100)

        # Get all unique EMA pairs
        all_ema_pairs = set()
        for mode_results in all_mode_results.values():
            for result in mode_results:
                all_ema_pairs.add(f"{result['ema_short']}/{result['ema_long']}")

        # Sort EMA pairs
        sorted_ema_pairs = sorted(all_ema_pairs)

        # Define metrics to compare
        metrics = ["return_pct", "sharpe_ratio", "win_rate", "profit_factor", "max_drawdown_pct"]

        # Print comparison for each EMA pair and metric
        for ema_pair in sorted_ema_pairs:
            for metric in metrics:
                row = f"{ema_pair:<10} {metric.replace('_', ' ').title():<15}"

                for mode in modes:
                    # Find the result for this EMA pair
                    pair_result = next((r for r in all_mode_results[mode] if f"{r['ema_short']}/{r['ema_long']}" == ema_pair), None)

                    if pair_result and metric in pair_result:
                        value = pair_result[metric]

                        # Format based on metric type
                        if metric in ['win_rate']:
                            formatted_value = f"{value*100:.1f}%"
                        elif metric in ['return_pct', 'max_drawdown_pct']:
                            formatted_value = f"{value:.1f}%"
                        elif metric in ['profit_factor']:
                            formatted_value = f"{value:.2f}"
                        else:
                            formatted_value = f"{value:.2f}"

                        row += f"{formatted_value:<15}"
                    else:
                        row += f"{'N/A':<15}"

                print(row)

            # Add separator between EMA pairs
            print("-" * 100)

        return all_mode_results, all_mode_trades

    except Exception as e:
        logger.error(f"Error in comparative analysis: {e}")
        raise

def main() -> int:
    """Main entry point"""
    # Start health check server
    execution_settings = get_execution_settings()
    health_port = int(os.environ.get('HEALTH_PORT', execution_settings['health_port']))
    start_health_check_server(port=health_port)
    logger.info(f"Health check server started on port {health_port}")

    args = parse_arguments()

    # Set debug logging if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)

    try:
        # Load configuration
        config = get_config(args.config) if not args.no_config else {
            'execution': {
                'mode': constants.DEFAULT_EXECUTION_MODE,
                'seed': constants.DEFAULT_SEED,
                'health_port': constants.DEFAULT_HEALTH_PORT
            }
        }

        # Set execution parameters
        deterministic = args.deterministic
        sequential = args.sequential
        seed = args.seed

        # Log the execution mode
        execution_type = "deterministic" if deterministic else "standard"
        execution_method = "sequential" if sequential else "parallel"
        logger.info(f"Execution mode: {execution_type} {execution_method} (seed={seed})")

        # Handle validation modes
        if args.quick_validate:
            logger.info("Running quick validation...")
            from backtest.quick_validate import run_quick_validation
            run_quick_validation(args.config, args.data, seed)
            logger.info("Quick validation completed.")
            return 0

        if args.cross_validate:
            logger.info("Running full cross-validation...")
            from backtest.cross_validate import run_parallel_validation
            run_parallel_validation(args.config, args.data, seed)
            logger.info("Cross-validation completed.")
            return 0

        # Determine analysis mode based on arguments
        flat_results = []

        # Run all combinations analysis
        if args.all_combinations:
            all_results, _ = run_all_combinations_analysis(
                config_path=args.config,
                data_path=args.data,
                symbol=args.symbol,
                deterministic=deterministic,
                sequential=sequential,
                seed=seed,
                cross_validate=False
            )
            flat_results = all_results

        # Run comparative analysis
        elif args.compare:
            if args.compare == 'modes':
                # Compare trading modes
                all_results, _ = run_comparative_analysis(
                    config_path=args.config,
                    data_path=args.data,
                    symbol=args.symbol,
                    output_dir=args.output
                )
                # Flatten results
                flat_results = []
                for mode, results in all_results.items():
                    for result in results:
                        result['trading_mode'] = mode
                        flat_results.append(result)

            elif args.compare == 'patterns':
                # Compare candle patterns
                all_results, _ = run_comparative_patterns_analysis(
                    config_path=args.config,
                    data_path=args.data,
                    symbol=args.symbol,
                    output_dir=args.output,
                    mode=args.mode
                )
                # Flatten results
                flat_results = []
                for pattern, results in all_results.items():
                    for result in results:
                        result['pattern_length'] = pattern
                        flat_results.append(result)

        # Run single strategy
        else:
            flat_results, _ = run_strategy(
                config_path=args.config,
                data_path=args.data,
                symbol=args.symbol,
                output_dir=args.output,
                mode=args.mode,
                candle_pattern=args.candle_pattern
            )

        # Generate Excel report if requested
        if args.report and flat_results:
            config = get_config(args.config)
            report_file = create_consolidated_report(flat_results, config)
            logger.info(f"Consolidated Excel report generated: {report_file}")

        return 0
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
