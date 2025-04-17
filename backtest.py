from strategies.ema_ha import EMAHeikinAshiStrategy
from utils import load_config, load_data, save_results
from pathlib import Path
from tabulate import tabulate

def format_results_table(results_list):
    """Format backtest results into a table"""
    headers = ['EMA Pair', 'Total Trades', 'Win Rate', 'Profit Factor', 'PNL', 'Return %', 
              'Max DD%', 'Avg Monthly%', 'Sharpe Ratio']
    
    rows = []
    for result in results_list:
        rows.append([
            f"{result['ema_short']}/{result['ema_long']}",
            f"{result['total_trades']:,}",
            f"{result['win_rate']*100:.1f}%",
            f"{result['profit_factor']:.2f}",
            f"₹{result['total_profit']:,.0f}",
            f"{result['return_pct']:.1f}",
            f"{result['max_drawdown_pct']:.1f}",
            f"{result['monthly_returns_avg']:.1f}",
            f"{result['monthly_returns_avg']/result['monthly_returns_std']:.2f}" if result['monthly_returns_std'] != 0 else "N/A"
        ])
    
    return tabulate(rows, headers=headers, tablefmt='grid')

def find_best_pair(all_results):
    """Find the best performing EMA pair based on risk-adjusted returns"""
    best_result = max(all_results, key=lambda x: x['monthly_returns_avg'] / x['monthly_returns_std'] 
                     if x['monthly_returns_std'] != 0 else 0)
    
    return {
        'ema_pair': f"{best_result['ema_short']}/{best_result['ema_long']}",
        'return_pct': best_result['return_pct'],
        'sharpe': best_result['monthly_returns_avg'] / best_result['monthly_returns_std'],
        'win_rate': best_result['win_rate'],
        'profit_factor': best_result['profit_factor']
    }

def analyze_exit_reasons(trades):
    """Analyze trade exit reasons"""
    total_trades = len(trades)
    if total_trades == 0:
        return {'signal_exits_pct': 0, 'force_exits_pct': 0}
    
    signal_exits = sum(1 for t in trades if t['exit_reason'] == 'Signal')
    force_exits = sum(1 for t in trades if t['exit_reason'] == 'ForceExit')
    
    return {
        'signal_exits_pct': signal_exits / total_trades * 100,
        'force_exits_pct': force_exits / total_trades * 100
    }

def print_backtest_summary(results, trades):
    """Print detailed backtest summary"""
    exit_stats = analyze_exit_reasons(trades)
    
    print("\nExit Analysis:")
    print(f"Signal Exits: {exit_stats['signal_exits_pct']:.1f}%")
    print(f"Force Exits (15:15): {exit_stats['force_exits_pct']:.1f}%")
    
    # Rest of the summary printing...

def main():
    # Load configuration
    config = load_config()
    
    # Load market data
    data_file = Path(config['data']['data_folder']) / "NIFTY_1min.csv"
    data = load_data(data_file)
    
    print("\nBacktest Period:")
    print(f"Start: {data.attrs['start_date']}")
    print(f"End: {data.attrs['end_date']}")
    print(f"Total Trading Days: {data.attrs['total_days']:,}")
    print(f"Total Candles: {data.attrs['total_candles']:,}")
    print("\n")
    
    all_results = []
    
    # Run backtest for each EMA pair
    for ema_short, ema_long in config['strategy']['ema_pairs']:
        strategy = EMAHeikinAshiStrategy(ema_short, ema_long, config)  # Pass config here
        results, trades = strategy.backtest(data, initial_capital=config['backtest']['initial_capital'])
        save_results(results, trades, "NIFTY", ema_short, ema_long, data.attrs)
        all_results.append(results)
    
    # Print summary table
    print("BACKTEST RESULTS SUMMARY")
    print("=" * 80)
    print(format_results_table(all_results))
    print("\n")
    
    # Print best performing pair with additional metrics
    best = find_best_pair(all_results)
    print("BEST PERFORMING EMA PAIR")
    print("=" * 80)
    print(f"EMA Pair: {best['ema_pair']}")
    print(f"Total Return: {best['return_pct']:.1f}%")
    print(f"Sharpe Ratio: {best['sharpe']:.2f}")
    print("\n")

if __name__ == "__main__":
    main()
