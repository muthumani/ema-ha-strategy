"""
Excel report generation module.

This module provides functions to generate consolidated Excel reports
from backtest results across different configurations.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
import os
import logging
from datetime import datetime
from utils.logger import setup_logger
from utils.config_utils import get_config_value, get_backtest_date_range, get_symbol, get_market_session_times, get_risk_management, get_initial_capital

# Set up logger
logger = setup_logger(name="excel_report", log_level=logging.INFO)

def create_consolidated_report(all_results: List[Dict[str, Any]],
                              config: Dict[str, Any],
                              output_file: str = None) -> str:
    """
    Create a consolidated Excel report from backtest results.

    Args:
        all_results: List of backtest results
        config: Configuration dictionary
        output_file: Output file path (optional)

    Returns:
        Path to the generated Excel file
    """
    try:
        # Validate results to ensure they have all required keys
        valid_results = []
        required_keys = ['ema_short', 'ema_long', 'trading_mode', 'pattern_length', 'total_trades',
                        'win_rate', 'profit_factor', 'total_profit', 'return_pct', 'max_drawdown_pct']

        for result in all_results:
            if all(key in result for key in required_keys):
                valid_results.append(result)
            else:
                missing_keys = [key for key in required_keys if key not in result]
                logger.warning(f"Skipping result with missing keys: {missing_keys}. Result: {result}")

        # If no valid results, log warning and return
        if not valid_results:
            logger.warning("No valid results found for Excel report generation")
            return output_file if output_file else "No report generated"

        # Use valid results for report generation
        all_results = valid_results

        # Create a pandas Excel writer
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = config.get('data', {}).get('output_folder', 'data/reports')
            os.makedirs(output_dir, exist_ok=True)
            output_file = f"{output_dir}/consolidated_report_{timestamp}.xlsx"

        # Create Excel writer
        writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

        # Generate overview sheet
        _create_overview_sheet(writer, config, all_results)

        # Generate summary sheet
        _create_summary_sheet(writer, all_results)

        # Generate detailed results sheet
        _create_detailed_results_sheet(writer, all_results)

        # Generate best performers sheet
        _create_best_performers_sheet(writer, all_results)

        # Generate comparison sheets
        _create_ema_comparison_sheet(writer, all_results)
        _create_mode_comparison_sheet(writer, all_results)
        _create_pattern_comparison_sheet(writer, all_results)

        # Re-enable dashboard sheet with improved error handling
        try:
            logger.info("Attempting to create dashboard sheet with improved error handling")
            _create_dashboard_sheet(writer, all_results)
            logger.info("Dashboard sheet created successfully")
        except Exception as e:
            logger.error(f"Error creating dashboard sheet, skipping: {e}")

        # Save the Excel file
        writer.close()

        logger.info(f"Consolidated report saved to {output_file}")
        return output_file

    except Exception as e:
        logger.error(f"Error creating consolidated report: {e}")
        # Try to close the writer if it exists
        try:
            if 'writer' in locals():
                writer.close()
        except:
            pass
        raise

def _create_overview_sheet(writer: pd.ExcelWriter, config: Dict[str, Any], all_results: List[Dict[str, Any]] = None):
    """Create overview sheet with backtest configuration details"""
    try:
        # Get symbol from config
        symbol = get_symbol()

        # Get trading session times from config
        session_times = get_market_session_times()
        market_open = session_times['market_open']
        market_close = session_times['market_close']
        market_entry = session_times['market_entry']
        force_exit = session_times['force_exit']

        # Get risk management settings from config
        risk_config = get_risk_management()
        stop_loss = f"{risk_config['stop_loss_pct']}%" if risk_config['use_stop_loss'] else "Disabled"
        trailing_stop = f"{risk_config['trailing_stop_pct']}%" if risk_config['use_trailing_stop'] else "Disabled"

        # Get backtest settings from config
        initial_capital = get_initial_capital()
        position_size = get_config_value('backtest.position_size', 1.0)
        commission = get_config_value('backtest.commission_pct', 0.05)

        # Get Heikin Ashi pattern settings from config
        confirmation_candles = get_config_value('strategy.ha_patterns.confirmation_candles', [])
        confirmation_candles_str = ", ".join([str(c) for c in confirmation_candles]) if confirmation_candles else "None"

        # Get backtest date range from results if available, otherwise use config
        backtest_date_range = get_backtest_date_range()  # Default from config

        if all_results and len(all_results) > 0:
            # Try to get date range from the first result
            first_result = all_results[0]
            if 'backtest_period' in first_result:
                start_date = first_result['backtest_period'].get('start_date')
                end_date = first_result['backtest_period'].get('end_date')
                if start_date and end_date:
                    backtest_date_range = f"{start_date} to {end_date}"
                    logger.info(f"Using actual backtest date range: {backtest_date_range}")

        # Create overview data
        overview_data = {
            'Parameter': [
                'Symbol',
                'Backtest Date Range',
                'Market Open',
                'Market Close',
                'Entry Time',
                'Force Exit Time',
                'Stop Loss',
                'Trailing Stop',
                'Initial Capital',
                'Position Size',
                'Commission',
                'Confirmation Candles',
                'Report Generated'
            ],
            'Value': [
                symbol,
                backtest_date_range,
                market_open,
                market_close,
                market_entry,
                force_exit,
                stop_loss,
                trailing_stop,
                f"Rs. {initial_capital:,.2f}",
                f"{position_size:.2f}",
                f"{commission:.2f}%",
                confirmation_candles_str,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ]
        }

        # Create DataFrame
        df_overview = pd.DataFrame(overview_data)

        # Write to Excel
        df_overview.to_excel(writer, sheet_name='Overview', index=False)

        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Overview']

        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D7E4BC',
            'border': 1
        })

        # Format header row
        for col_num, value in enumerate(df_overview.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Adjust column widths
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 25)

        # Add title
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter'
        })
        worksheet.merge_range('A1:B1', 'Backtest Configuration', title_format)
        worksheet.write_string(1, 0, 'Parameter', header_format)
        worksheet.write_string(1, 1, 'Value', header_format)

        # Shift data down by 1 row
        for i in range(len(df_overview)):
            worksheet.write_string(i+2, 0, df_overview.iloc[i, 0])
            worksheet.write_string(i+2, 1, df_overview.iloc[i, 1])

    except Exception as e:
        logger.error(f"Error creating overview sheet: {e}")
        raise

def _create_summary_sheet(writer: pd.ExcelWriter, all_results: List[Dict[str, Any]]):
    """Create summary sheet with aggregated results"""
    try:
        # Extract relevant data for summary
        summary_data = []

        for result in all_results:
            ema_pair = f"{result['ema_short']}/{result['ema_long']}"
            trading_mode = result.get('trading_mode', 'SWING')

            # Determine pattern type
            pattern_info = "None"
            if 'pattern_length' in result:
                pattern_length = result['pattern_length']
                if isinstance(pattern_length, str):
                    pattern_info = f"{pattern_length}-Candle" if pattern_length != 'None' else "None"
                else:
                    pattern_info = f"{pattern_length}-Candle"

            summary_data.append({
                'EMA Pair': ema_pair,
                'Trading Mode': trading_mode,
                'Pattern': pattern_info,
                'Trades': result['total_trades'],
                'Win Rate': result['win_rate'] * 100,
                'Profit Factor': result['profit_factor'],
                'Total Profit': result['total_profit'],
                'Return %': result['return_pct'],
                'Max Drawdown %': result['max_drawdown_pct'],
                'Sharpe Ratio': result.get('sharpe_ratio', 0)
            })

        # Create DataFrame
        df_summary = pd.DataFrame(summary_data)

        # Sort by Return % descending
        df_summary = df_summary.sort_values('Return %', ascending=False)

        # Write to Excel
        df_summary.to_excel(writer, sheet_name='Summary', index=False)

        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Summary']

        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D7E4BC',
            'border': 1
        })

        # Format header row
        for col_num, value in enumerate(df_summary.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Add number formats
        num_format = workbook.add_format({'num_format': '#,##0'})
        pct_format = workbook.add_format({'num_format': '0.0%'})
        decimal_format = workbook.add_format({'num_format': '0.00'})
        money_format = workbook.add_format({'num_format': '₹#,##0.00'})

        # Apply formats to columns
        worksheet.set_column('A:A', 10)  # EMA Pair
        worksheet.set_column('B:B', 12)  # Trading Mode
        worksheet.set_column('C:C', 12)  # Pattern
        worksheet.set_column('D:D', 10, num_format)  # Trades
        worksheet.set_column('E:E', 10, pct_format)  # Win Rate
        worksheet.set_column('F:F', 12, decimal_format)  # Profit Factor
        worksheet.set_column('G:G', 15, money_format)  # Total Profit
        worksheet.set_column('H:H', 10, pct_format)  # Return %
        worksheet.set_column('I:I', 15, pct_format)  # Max Drawdown %
        worksheet.set_column('J:J', 12, decimal_format)  # Sharpe Ratio

        # Apply formats to cells directly
        for i, row in enumerate(df_summary.values, start=1):
            # Apply formats to numeric columns
            worksheet.write_number(i, 3, row[3])  # Trades
            worksheet.write_number(i, 4, row[4] / 100)  # Win Rate as decimal
            worksheet.write_number(i, 5, row[5])  # Profit Factor
            worksheet.write_number(i, 6, row[6])  # Total Profit
            worksheet.write_number(i, 7, row[7] / 100)  # Return % as decimal
            worksheet.write_number(i, 8, row[8] / 100)  # Max Drawdown % as decimal
            worksheet.write_number(i, 9, row[9])  # Sharpe Ratio

    except Exception as e:
        logger.error(f"Error creating summary sheet: {e}")
        raise

def _create_detailed_results_sheet(writer: pd.ExcelWriter, all_results: List[Dict[str, Any]]):
    """Create detailed results sheet with all metrics"""
    try:
        # Extract all results data
        results_data = []

        for result in all_results:
            ema_pair = f"{result['ema_short']}/{result['ema_long']}"
            trading_mode = result.get('trading_mode', 'SWING')

            # Determine pattern type
            pattern_info = "None"
            if 'pattern_length' in result:
                pattern_length = result['pattern_length']
                if isinstance(pattern_length, str):
                    pattern_info = f"{pattern_length}-Candle" if pattern_length != 'None' else "None"
                else:
                    pattern_info = f"{pattern_length}-Candle"

            # Extract exit reasons
            exit_reasons = result.get('exit_reasons', {})
            signal_exits = exit_reasons.get('Signal', 0)
            trailing_stop_exits = exit_reasons.get('TrailingStop', 0)
            stop_loss_exits = exit_reasons.get('StopLoss', 0)
            force_exits = exit_reasons.get('ForceExit', 0)

            # Calculate exit percentages
            total_trades = result['total_trades']
            signal_exits_pct = signal_exits / total_trades * 100 if total_trades > 0 else 0
            trailing_stop_exits_pct = trailing_stop_exits / total_trades * 100 if total_trades > 0 else 0
            stop_loss_exits_pct = stop_loss_exits / total_trades * 100 if total_trades > 0 else 0
            force_exits_pct = force_exits / total_trades * 100 if total_trades > 0 else 0

            # Add to results data
            results_data.append({
                'EMA Pair': ema_pair,
                'Trading Mode': trading_mode,
                'Pattern': pattern_info,
                'Total Trades': total_trades,
                'Winning Trades': result.get('winning_trades', 0),
                'Win Rate %': result['win_rate'] * 100,
                'Profit Factor': result['profit_factor'],
                'Total Profit': result['total_profit'],
                'Return %': result['return_pct'],
                'Max Drawdown %': result['max_drawdown_pct'],
                'Sharpe Ratio': result.get('sharpe_ratio', 0),
                'Monthly Returns Avg': result.get('monthly_returns_avg', 0) * 100,
                'Monthly Returns Std': result.get('monthly_returns_std', 0) * 100,
                'Profitable Months': result.get('profitable_months', 0),
                'Max Monthly Profit %': result.get('max_monthly_profit', 0) * 100,
                'Max Monthly Loss %': result.get('max_monthly_loss', 0) * 100,
                'Signal Exits': signal_exits,
                'Signal Exits %': signal_exits_pct,
                'Trailing Stop Exits': trailing_stop_exits,
                'Trailing Stop Exits %': trailing_stop_exits_pct,
                'Stop Loss Exits': stop_loss_exits,
                'Stop Loss Exits %': stop_loss_exits_pct,
                'Force Exits': force_exits,
                'Force Exits %': force_exits_pct
            })

        # Create DataFrame
        df_results = pd.DataFrame(results_data)

        # Sort by Return % descending
        df_results = df_results.sort_values('Return %', ascending=False)

        # Write to Excel
        df_results.to_excel(writer, sheet_name='Detailed Results', index=False)

        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Detailed Results']

        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D7E4BC',
            'border': 1
        })

        # Format header row
        for col_num, value in enumerate(df_results.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Set column widths
        for i, col in enumerate(df_results.columns):
            col_width = max(len(col) + 2, 12)
            worksheet.set_column(i, i, col_width)

    except Exception as e:
        logger.error(f"Error creating detailed results sheet: {e}")
        raise

def _create_best_performers_sheet(writer: pd.ExcelWriter, all_results: List[Dict[str, Any]]):
    """Create best performers sheet with top results by different metrics"""
    try:
        # Create DataFrame from results
        df = pd.DataFrame(all_results)

        # Add EMA pair and pattern columns
        df['EMA Pair'] = df.apply(lambda x: f"{x['ema_short']}/{x['ema_long']}", axis=1)
        def get_pattern_str(row):
            if 'pattern_length' in row:
                pattern_length = row['pattern_length']
                if isinstance(pattern_length, str):
                    return f"{pattern_length}-Candle" if pattern_length != 'None' else "None"
                else:
                    return f"{pattern_length}-Candle"
            return "None"

        df['Pattern'] = df.apply(get_pattern_str, axis=1)

        # Create best performers data
        best_data = []

        # Best by Sharpe Ratio
        best_sharpe = df.loc[df['sharpe_ratio'].idxmax()] if 'sharpe_ratio' in df.columns and not df.empty else None
        if best_sharpe is not None:
            best_data.append({
                'Metric': 'Best Sharpe Ratio',
                'EMA Pair': best_sharpe['EMA Pair'],
                'Trading Mode': best_sharpe.get('trading_mode', 'SWING'),
                'Pattern': best_sharpe['Pattern'],
                'Value': best_sharpe.get('sharpe_ratio', 0),
                'Win Rate': best_sharpe['win_rate'] * 100,
                'Return %': best_sharpe['return_pct'],
                'Max Drawdown %': best_sharpe['max_drawdown_pct']
            })

        # Best by Return %
        best_return = df.loc[df['return_pct'].idxmax()] if not df.empty else None
        if best_return is not None:
            best_data.append({
                'Metric': 'Best Return %',
                'EMA Pair': best_return['EMA Pair'],
                'Trading Mode': best_return.get('trading_mode', 'SWING'),
                'Pattern': best_return['Pattern'],
                'Value': best_return['return_pct'],
                'Win Rate': best_return['win_rate'] * 100,
                'Return %': best_return['return_pct'],
                'Max Drawdown %': best_return['max_drawdown_pct']
            })

        # Best by Win Rate
        best_win_rate = df.loc[df['win_rate'].idxmax()] if not df.empty else None
        if best_win_rate is not None:
            best_data.append({
                'Metric': 'Best Win Rate',
                'EMA Pair': best_win_rate['EMA Pair'],
                'Trading Mode': best_win_rate.get('trading_mode', 'SWING'),
                'Pattern': best_win_rate['Pattern'],
                'Value': best_win_rate['win_rate'] * 100,
                'Win Rate': best_win_rate['win_rate'] * 100,
                'Return %': best_win_rate['return_pct'],
                'Max Drawdown %': best_win_rate['max_drawdown_pct']
            })

        # Best by Profit Factor
        best_profit_factor = df.loc[df['profit_factor'].idxmax()] if not df.empty else None
        if best_profit_factor is not None:
            best_data.append({
                'Metric': 'Best Profit Factor',
                'EMA Pair': best_profit_factor['EMA Pair'],
                'Trading Mode': best_profit_factor.get('trading_mode', 'SWING'),
                'Pattern': best_profit_factor['Pattern'],
                'Value': best_profit_factor['profit_factor'],
                'Win Rate': best_profit_factor['win_rate'] * 100,
                'Return %': best_profit_factor['return_pct'],
                'Max Drawdown %': best_profit_factor['max_drawdown_pct']
            })

        # Best by Lowest Max Drawdown
        if not df.empty:
            # Filter out zero drawdowns which might be from failed backtests
            df_nonzero_dd = df[df['max_drawdown_pct'] > 0]
            if not df_nonzero_dd.empty:
                best_drawdown = df_nonzero_dd.loc[df_nonzero_dd['max_drawdown_pct'].idxmin()]
                best_data.append({
                    'Metric': 'Lowest Max Drawdown',
                    'EMA Pair': best_drawdown['EMA Pair'],
                    'Trading Mode': best_drawdown.get('trading_mode', 'SWING'),
                    'Pattern': best_drawdown['Pattern'],
                    'Value': best_drawdown['max_drawdown_pct'],
                    'Win Rate': best_drawdown['win_rate'] * 100,
                    'Return %': best_drawdown['return_pct'],
                    'Max Drawdown %': best_drawdown['max_drawdown_pct']
                })

        # Create DataFrame
        df_best = pd.DataFrame(best_data)

        # Write to Excel
        df_best.to_excel(writer, sheet_name='Best Performers', index=False)

        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Best Performers']

        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D7E4BC',
            'border': 1
        })

        # Format header row
        for col_num, value in enumerate(df_best.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Set column widths
        worksheet.set_column('A:A', 20)  # Metric
        worksheet.set_column('B:B', 10)  # EMA Pair
        worksheet.set_column('C:C', 12)  # Trading Mode
        worksheet.set_column('D:D', 12)  # Pattern
        worksheet.set_column('E:H', 15)  # Values

    except Exception as e:
        logger.error(f"Error creating best performers sheet: {e}")
        raise

def _create_ema_comparison_sheet(writer: pd.ExcelWriter, all_results: List[Dict[str, Any]]):
    """Create EMA comparison sheet"""
    try:
        # Create DataFrame from results
        df = pd.DataFrame(all_results)

        # Add EMA pair column
        df['EMA Pair'] = df.apply(lambda x: f"{x['ema_short']}/{x['ema_long']}", axis=1)

        # Group by EMA pair and calculate averages
        ema_groups = df.groupby('EMA Pair').agg({
            'total_trades': 'mean',
            'win_rate': 'mean',
            'profit_factor': 'mean',
            'total_profit': 'mean',
            'return_pct': 'mean',
            'max_drawdown_pct': 'mean',
            'sharpe_ratio': 'mean'
        }).reset_index()

        # Rename columns
        ema_groups.columns = [
            'EMA Pair',
            'Avg Trades',
            'Avg Win Rate',
            'Avg Profit Factor',
            'Avg Total Profit',
            'Avg Return %',
            'Avg Max Drawdown %',
            'Avg Sharpe Ratio'
        ]

        # Sort by average return
        ema_groups = ema_groups.sort_values('Avg Return %', ascending=False)

        # Write to Excel
        ema_groups.to_excel(writer, sheet_name='EMA Comparison', index=False)

        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['EMA Comparison']

        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D7E4BC',
            'border': 1
        })

        # Format header row
        for col_num, value in enumerate(ema_groups.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Set column widths
        for i, col in enumerate(ema_groups.columns):
            col_width = max(len(col) + 2, 12)
            worksheet.set_column(i, i, col_width)

    except Exception as e:
        logger.error(f"Error creating EMA comparison sheet: {e}")
        raise

def _create_mode_comparison_sheet(writer: pd.ExcelWriter, all_results: List[Dict[str, Any]]):
    """Create trading mode comparison sheet"""
    try:
        # Create DataFrame from results
        df = pd.DataFrame(all_results)

        # Check if trading_mode column exists
        if 'trading_mode' not in df.columns:
            # Skip this sheet if no trading mode data
            return

        # Group by trading mode and calculate averages
        mode_groups = df.groupby('trading_mode').agg({
            'total_trades': 'mean',
            'win_rate': 'mean',
            'profit_factor': 'mean',
            'total_profit': 'mean',
            'return_pct': 'mean',
            'max_drawdown_pct': 'mean',
            'sharpe_ratio': 'mean'
        }).reset_index()

        # Rename columns
        mode_groups.columns = [
            'Trading Mode',
            'Avg Trades',
            'Avg Win Rate',
            'Avg Profit Factor',
            'Avg Total Profit',
            'Avg Return %',
            'Avg Max Drawdown %',
            'Avg Sharpe Ratio'
        ]

        # Sort by average return
        mode_groups = mode_groups.sort_values('Avg Return %', ascending=False)

        # Write to Excel
        mode_groups.to_excel(writer, sheet_name='Mode Comparison', index=False)

        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Mode Comparison']

        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D7E4BC',
            'border': 1
        })

        # Format header row
        for col_num, value in enumerate(mode_groups.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Set column widths
        for i, col in enumerate(mode_groups.columns):
            col_width = max(len(col) + 2, 12)
            worksheet.set_column(i, i, col_width)

    except Exception as e:
        logger.error(f"Error creating mode comparison sheet: {e}")
        raise

def _create_pattern_comparison_sheet(writer: pd.ExcelWriter, all_results: List[Dict[str, Any]]):
    """Create pattern comparison sheet"""
    try:
        # Create DataFrame from results
        df = pd.DataFrame(all_results)

        # Add pattern column
        def get_pattern_str(row):
            if 'pattern_length' in row:
                pattern_length = row['pattern_length']
                if isinstance(pattern_length, str):
                    return f"{pattern_length}-Candle" if pattern_length != 'None' else "None"
                else:
                    return f"{pattern_length}-Candle"
            return "None"

        df['Pattern'] = df.apply(get_pattern_str, axis=1)

        # Group by pattern and calculate averages
        pattern_groups = df.groupby('Pattern').agg({
            'total_trades': 'mean',
            'win_rate': 'mean',
            'profit_factor': 'mean',
            'total_profit': 'mean',
            'return_pct': 'mean',
            'max_drawdown_pct': 'mean',
            'sharpe_ratio': 'mean'
        }).reset_index()

        # Rename columns
        pattern_groups.columns = [
            'Pattern',
            'Avg Trades',
            'Avg Win Rate',
            'Avg Profit Factor',
            'Avg Total Profit',
            'Avg Return %',
            'Avg Max Drawdown %',
            'Avg Sharpe Ratio'
        ]

        # Sort by average return
        pattern_groups = pattern_groups.sort_values('Avg Return %', ascending=False)

        # Write to Excel
        pattern_groups.to_excel(writer, sheet_name='Pattern Comparison', index=False)

        # Get workbook and worksheet objects
        workbook = writer.book
        worksheet = writer.sheets['Pattern Comparison']

        # Add formatting
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#D7E4BC',
            'border': 1
        })

        # Format header row
        for col_num, value in enumerate(pattern_groups.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Set column widths
        for i, col in enumerate(pattern_groups.columns):
            col_width = max(len(col) + 2, 12)
            worksheet.set_column(i, i, col_width)

    except Exception as e:
        logger.error(f"Error creating pattern comparison sheet: {e}")
        raise

def create_excel_report(output_file: str, all_results: List[Dict[str, Any]], all_trades: List[List[Dict[str, Any]]] = None) -> str:
    """
    Create an Excel report from backtest results.

    Args:
        output_file: Output file path
        all_results: List of backtest results
        all_trades: List of trades for each result (optional)

    Returns:
        Path to the generated Excel file
    """
    try:
        # Use the existing config from get_config() and just override the output folder
        from utils.config_utils import get_config
        config = get_config()

        # Ensure the output folder is set correctly
        if 'data' not in config:
            config['data'] = {}
        config['data']['output_folder'] = os.path.dirname(output_file)

        # Create consolidated report
        return create_consolidated_report(all_results, config, output_file)

    except Exception as e:
        logger.error(f"Error creating Excel report: {e}")
        raise

def _create_dashboard_sheet(writer: pd.ExcelWriter, all_results: List[Dict[str, Any]]):
    """Create a dashboard sheet with visualizations"""
    try:
        # Add debug logging
        logger.info(f"Dashboard sheet creation started with {len(all_results)} results")
        for i, result in enumerate(all_results):
            logger.info(f"Result {i}: {result.keys()}")

        # Create a copy of all_results to avoid modifying the original
        processed_results = []
        for result in all_results:
            # Create a copy of the result
            processed_result = result.copy()

            # Ensure pattern_length is properly handled
            if 'pattern_length' in processed_result:
                pattern_length = processed_result['pattern_length']
                logger.info(f"Pattern length: {pattern_length}, type: {type(pattern_length)}")
                # Convert to string if needed
                if not isinstance(pattern_length, str):
                    processed_result['pattern_length'] = str(pattern_length)
                # Ensure pattern_length is not None
                if processed_result['pattern_length'] is None:
                    processed_result['pattern_length'] = "None"

            processed_results.append(processed_result)

        # Create DataFrame from processed results
        logger.info("Creating DataFrame from processed results")
        df = pd.DataFrame(processed_results)

        # Skip dashboard creation if there are no results
        if df.empty:
            logger.warning("No results available for dashboard creation")
            return

        # Add a simplified version that doesn't rely on complex data structures
        workbook = writer.book
        worksheet = workbook.add_worksheet('Dashboard')

        # Add title
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 18,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D7E4BC',
            'border': 1
        })
        worksheet.merge_range('A1:O1', 'EMA-HA Strategy Performance Dashboard', title_format)

        # Create a simple summary table
        section_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'left',
            'valign': 'vcenter',
            'bg_color': '#E6F2D3',
            'border': 1
        })

        worksheet.merge_range('A3:H3', 'Performance Summary', section_format)

        # Write headers
        headers = ['EMA Pair', 'Trading Mode', 'Pattern', 'Return %', 'Win Rate', 'Profit Factor', 'Max DD %', 'Sharpe']
        for i, header in enumerate(headers):
            worksheet.write(4, i, header, workbook.add_format({'bold': True, 'bg_color': '#D7E4BC'}))

        # Write data
        for i, result in enumerate(all_results):
            ema_pair = f"{result['ema_short']}/{result['ema_long']}"
            pattern_length = result.get('pattern_length', 'None')
            pattern = f"{pattern_length}-Candle" if pattern_length != 'None' else "None"

            worksheet.write(i+5, 0, ema_pair)
            worksheet.write(i+5, 1, result.get('trading_mode', 'SWING'))
            worksheet.write(i+5, 2, pattern)
            worksheet.write(i+5, 3, result['return_pct'])
            worksheet.write(i+5, 4, result['win_rate'] * 100)
            worksheet.write(i+5, 5, result['profit_factor'])
            worksheet.write(i+5, 6, result['max_drawdown_pct'])
            worksheet.write(i+5, 7, result.get('sharpe_ratio', 0))

        # Create a simple bar chart for returns
        chart = workbook.add_chart({'type': 'column'})

        # Configure the chart
        chart.add_series({
            'name': 'Return %',
            'categories': ['Dashboard', 5, 0, 5 + len(all_results) - 1, 0],  # EMA Pair
            'values': ['Dashboard', 5, 3, 5 + len(all_results) - 1, 3],      # Return %
        })

        chart.set_title({'name': 'Returns by EMA Pair'})
        chart.set_x_axis({'name': 'EMA Pair'})
        chart.set_y_axis({'name': 'Return %'})

        # Insert the chart
        worksheet.insert_chart('A15', chart, {'x_offset': 25, 'y_offset': 10, 'x_scale': 1.5, 'y_scale': 1.5})

        # Create pattern data for pattern comparison chart
        # Group by pattern and calculate averages
        try:
            logger.info("Creating Pattern column")
            def get_pattern_str(row):
                try:
                    if 'pattern_length' in row:
                        pattern_length = row['pattern_length']
                        logger.info(f"Processing pattern_length: {pattern_length}, type: {type(pattern_length)}")
                        if pattern_length is None:
                            return "None"
                        elif isinstance(pattern_length, str):
                            return f"{pattern_length}-Candle" if pattern_length != 'None' else "None"
                        else:
                            return f"{pattern_length}-Candle"
                    return "None"
                except Exception as e:
                    logger.error(f"Error in get_pattern_str: {e}, row: {row}")
                    return "None"

            df['Pattern'] = df.apply(get_pattern_str, axis=1)
            logger.info("Pattern column created successfully")
        except Exception as e:
            logger.error(f"Error creating Pattern column: {e}")
            # Create a simple Pattern column as fallback
            df['Pattern'] = "None"

        pattern_data = df.groupby('Pattern').agg({
            'return_pct': 'mean',
            'win_rate': 'mean',
            'profit_factor': 'mean',
            'sharpe_ratio': 'mean',
            'max_drawdown_pct': 'mean'
        }).reset_index()

        # Create pattern chart
        pattern_chart = workbook.add_chart({'type': 'column'})

        # Write data for the chart
        worksheet.write_string(52, 0, 'Pattern')
        worksheet.write_string(52, 1, 'Return %')
        worksheet.write_string(52, 2, 'Win Rate')
        worksheet.write_string(52, 3, 'Profit Factor')
        worksheet.write_string(52, 4, 'Sharpe Ratio')
        worksheet.write_string(52, 5, 'Max Drawdown %')

        for i, row in enumerate(pattern_data.itertuples(), start=53):
            worksheet.write_string(i, 0, row.Pattern)
            worksheet.write_number(i, 1, row.return_pct)
            worksheet.write_number(i, 2, row.win_rate * 100)
            worksheet.write_number(i, 3, row.profit_factor)
            worksheet.write_number(i, 4, row.sharpe_ratio)
            worksheet.write_number(i, 5, row.max_drawdown_pct)

        # Configure the chart
        pattern_chart.add_series({
            'name': 'Return %',
            'categories': ['Dashboard', 53, 0, 53 + len(pattern_data) - 1, 0],
            'values': ['Dashboard', 53, 1, 53 + len(pattern_data) - 1, 1],
        })

        pattern_chart.add_series({
            'name': 'Win Rate',
            'categories': ['Dashboard', 53, 0, 53 + len(pattern_data) - 1, 0],
            'values': ['Dashboard', 53, 2, 53 + len(pattern_data) - 1, 2],
        })

        pattern_chart.add_series({
            'name': 'Sharpe Ratio',
            'categories': ['Dashboard', 53, 0, 53 + len(pattern_data) - 1, 0],
            'values': ['Dashboard', 53, 4, 53 + len(pattern_data) - 1, 4],
        })

        pattern_chart.set_title({'name': 'Performance by Pattern'})
        pattern_chart.set_x_axis({'name': 'Pattern'})
        pattern_chart.set_y_axis({'name': 'Value'})
        pattern_chart.set_style(11)

        # Insert the chart into the worksheet
        worksheet.insert_chart('A57', pattern_chart, {'x_offset': 25, 'y_offset': 10, 'x_scale': 1.5, 'y_scale': 1.5})

        # 4. Top 5 Combinations Table
        worksheet.merge_range('I3:O3', 'Top 5 Combinations by Return', section_format)

        # Sort by return and get top 5
        top_combinations = df.sort_values('return_pct', ascending=False).head(5)

        # Write headers
        worksheet.write_string(4, 8, 'Combination')
        worksheet.write_string(4, 9, 'Return %')
        worksheet.write_string(4, 10, 'Win Rate')
        worksheet.write_string(4, 11, 'Profit Factor')
        worksheet.write_string(4, 12, 'Sharpe Ratio')
        worksheet.write_string(4, 13, 'Max DD %')
        worksheet.write_string(4, 14, 'Trades')

        # Write data
        try:
            logger.info("Writing top combinations data")
            for i, row in enumerate(top_combinations.itertuples(), start=5):
                try:
                    # Create combination string manually
                    combo = f"{row.ema_short}/{row.ema_long} {row.trading_mode} {row.Pattern}"
                    worksheet.write_string(i, 8, combo)
                    worksheet.write_number(i, 9, row.return_pct)
                    worksheet.write_number(i, 10, row.win_rate * 100)
                    worksheet.write_number(i, 11, row.profit_factor)
                    worksheet.write_number(i, 12, row.sharpe_ratio)
                    worksheet.write_number(i, 13, row.max_drawdown_pct)
                    worksheet.write_number(i, 14, row.total_trades)
                except Exception as e:
                    logger.error(f"Error writing top combination row {i}: {e}")
        except Exception as e:
            logger.error(f"Error writing top combinations data: {e}")

        # 5. Risk-Adjusted Performance Chart (Scatter Plot)
        worksheet.merge_range('I27:O27', 'Risk-Adjusted Performance', section_format)

        # Create a scatter chart
        scatter_chart = workbook.add_chart({'type': 'scatter'})

        # Write data for the chart
        worksheet.write_string(28, 8, 'Combination')
        worksheet.write_string(28, 9, 'Return %')
        worksheet.write_string(28, 10, 'Max Drawdown %')
        worksheet.write_string(28, 11, 'Sharpe Ratio')
        worksheet.write_string(28, 12, 'Trades')

        # Get top 10 by Sharpe ratio
        top_sharpe = df.sort_values('sharpe_ratio', ascending=False).head(10)

        try:
            logger.info("Writing top sharpe data")
            for i, row in enumerate(top_sharpe.itertuples(), start=29):
                try:
                    # Create combination string manually
                    combo = f"{row.ema_short}/{row.ema_long} {row.trading_mode} {row.Pattern}"
                    worksheet.write_string(i, 8, combo)
                    worksheet.write_number(i, 9, row.return_pct)
                    worksheet.write_number(i, 10, row.max_drawdown_pct)
                    worksheet.write_number(i, 11, row.sharpe_ratio)
                    worksheet.write_number(i, 12, row.total_trades)
                except Exception as e:
                    logger.error(f"Error writing top sharpe row {i}: {e}")
        except Exception as e:
            logger.error(f"Error writing top sharpe data: {e}")

        # Configure the chart
        try:
            logger.info("Configuring scatter chart")
            logger.info(f"Top sharpe type: {type(top_sharpe)}")
            logger.info(f"Top sharpe length: {len(top_sharpe)}")

            # Check if top_sharpe is empty
            if len(top_sharpe) == 0:
                logger.warning("No data for scatter chart, using dummy data")
                # Add dummy data point
                worksheet.write_string(29, 8, "No Data")
                worksheet.write_number(29, 9, 0)
                worksheet.write_number(29, 10, 0)
                worksheet.write_number(29, 11, 0)
                worksheet.write_number(29, 12, 0)

                scatter_chart.add_series({
                    'name': 'No Data',
                    'categories': ['Dashboard', 29, 10, 29, 10],
                    'values': ['Dashboard', 29, 9, 29, 9],
                    'marker': {'type': 'circle', 'size': 10},
                })
            else:
                scatter_chart.add_series({
                    'name': 'Combinations',
                    'categories': ['Dashboard', 29, 10, 29 + len(top_sharpe) - 1, 10],  # Max Drawdown
                    'values': ['Dashboard', 29, 9, 29 + len(top_sharpe) - 1, 9],  # Return
                    'marker': {'type': 'circle', 'size': 10},
                    'data_labels': {'value': True},  # Removed 'custom' which might be causing issues
                })
        except Exception as e:
            logger.error(f"Error configuring scatter chart: {e}")
            # Add a simple series without custom options
            scatter_chart.add_series({
                'name': 'Combinations',
                'categories': ['Dashboard', 29, 10, 29, 10],  # Just use one point
                'values': ['Dashboard', 29, 9, 29, 9],
            })

        scatter_chart.set_title({'name': 'Return vs Risk (Max Drawdown)'})
        scatter_chart.set_x_axis({'name': 'Max Drawdown %', 'reverse': True})  # Reverse so lower drawdown is better
        scatter_chart.set_y_axis({'name': 'Return %'})
        scatter_chart.set_style(11)

        # Insert the chart into the worksheet
        worksheet.insert_chart('I33', scatter_chart, {'x_offset': 25, 'y_offset': 10, 'x_scale': 1.5, 'y_scale': 1.5})

        # 6. Best Combination Details
        worksheet.merge_range('I51:O51', 'Best Combination Details', section_format)

        try:
            logger.info("Writing best combination details")
            # Get the best combination by Sharpe ratio
            best_combo = df.loc[df['sharpe_ratio'].idxmax()] if not df.empty else None

            if best_combo is not None:
                try:
                    # Write headers and data
                    metrics = [
                        'EMA Pair', 'Trading Mode', 'Pattern', 'Return %', 'Win Rate',
                        'Profit Factor', 'Sharpe Ratio', 'Max Drawdown %', 'Total Trades',
                        'Winning Trades', 'Monthly Avg Return', 'Monthly Std Dev'
                    ]

                    # Create EMA Pair string
                    ema_pair = f"{best_combo['ema_short']}/{best_combo['ema_long']}"

                    # Get trading mode with fallback
                    trading_mode = best_combo['trading_mode'] if 'trading_mode' in best_combo else 'SWING'

                    # Log best combo details for debugging
                    logger.info(f"Best combo: {best_combo}")
                    logger.info(f"Best combo type: {type(best_combo)}")

                    # Check if best_combo is a pandas Series or dict-like object
                    if hasattr(best_combo, 'items'):
                        for key, value in best_combo.items():
                            logger.info(f"Key: {key}, Value: {value}, Type: {type(value)}")
                    else:
                        logger.info(f"Best combo is not a dict-like object, it's a {type(best_combo)}")

                    # Safely get Pattern value
                    pattern_value = "None"
                    if 'Pattern' in best_combo:
                        pattern_value = best_combo['Pattern']

                    values = [
                        ema_pair,
                        trading_mode,
                        pattern_value,
                        f"{best_combo['return_pct']:.2f}%",
                        f"{best_combo['win_rate']*100:.2f}%",
                        f"{best_combo['profit_factor']:.2f}",
                        f"{best_combo['sharpe_ratio']:.2f}",
                        f"{best_combo['max_drawdown_pct']:.2f}%",
                        str(best_combo['total_trades']),
                        str(int(best_combo['total_trades'] * best_combo['win_rate'])),
                        f"{best_combo.get('monthly_returns_avg', 0)*100:.2f}%" if 'monthly_returns_avg' in best_combo else "N/A",
                        f"{best_combo.get('monthly_returns_std', 0)*100:.2f}%" if 'monthly_returns_std' in best_combo else "N/A"
                    ]

                    for i, (metric, value) in enumerate(zip(metrics, values)):
                        worksheet.write_string(52 + i, 8, metric)
                        worksheet.write_string(52 + i, 9, value)
                except Exception as e:
                    logger.error(f"Error writing best combination details: {e}")
        except Exception as e:
            logger.error(f"Error getting best combination: {e}")

    except Exception as e:
        logger.error(f"Error creating dashboard sheet: {e}")
        raise
