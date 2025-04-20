#!/usr/bin/env python
"""
Test data generator for EMA-HA Strategy acceptance testing.
This script generates synthetic market data for testing purposes.
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import argparse

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Generate synthetic market data for testing')
    parser.add_argument('--output', default='data/market_data/test_data.csv', help='Output file path')
    parser.add_argument('--days', type=int, default=30, help='Number of days to generate')
    parser.add_argument('--interval', type=int, default=1, help='Interval in minutes')
    parser.add_argument('--volatility', type=float, default=0.01, help='Price volatility')
    parser.add_argument('--seed', type=int, default=42, help='Random seed for reproducibility')
    return parser.parse_args()

def generate_market_data(days=30, interval=1, volatility=0.01, seed=42):
    """Generate synthetic market data"""
    # Set random seed for reproducibility
    np.random.seed(seed)
    
    # Define market hours (9:15 AM to 3:30 PM)
    market_open = datetime.strptime('09:15:00', '%H:%M:%S').time()
    market_close = datetime.strptime('15:30:00', '%H:%M:%S').time()
    
    # Calculate number of candles per day
    minutes_per_day = ((market_close.hour - market_open.hour) * 60 + 
                       (market_close.minute - market_open.minute))
    candles_per_day = minutes_per_day // interval
    
    # Generate timestamps
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=days)
    timestamps = []
    
    for day in range(days):
        current_date = start_date + timedelta(days=day)
        # Skip weekends
        if current_date.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            continue
        
        for candle in range(candles_per_day):
            candle_time = datetime.combine(
                current_date.date(),
                market_open
            ) + timedelta(minutes=candle * interval)
            
            if candle_time.time() <= market_close:
                timestamps.append(candle_time)
    
    # Generate price data
    num_candles = len(timestamps)
    initial_price = 18000.0  # Starting price (similar to NIFTY)
    
    # Generate random walk for close prices
    close_prices = [initial_price]
    for i in range(1, num_candles):
        # Random price change with drift
        price_change = np.random.normal(0, volatility) * close_prices[-1]
        # Add some trend
        trend = 0.0001 * close_prices[-1] * np.sin(i / 100)
        new_price = close_prices[-1] + price_change + trend
        close_prices.append(max(new_price, 0.1 * initial_price))  # Ensure price doesn't go too low
    
    # Generate OHLC data
    data = []
    for i, timestamp in enumerate(timestamps):
        close = close_prices[i]
        # Generate intracandle volatility
        high = close * (1 + abs(np.random.normal(0, volatility/2)))
        low = close * (1 - abs(np.random.normal(0, volatility/2)))
        
        # Ensure high is always highest and low is always lowest
        if i > 0:
            open_price = close_prices[i-1]
        else:
            open_price = close * (1 + np.random.normal(0, volatility/4))
        
        # Adjust high and low if needed
        high = max(high, open_price, close)
        low = min(low, open_price, close)
        
        data.append({
            'date': timestamp,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': int(np.random.normal(1000000, 500000))  # Random volume
        })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    return df

def main():
    """Main entry point"""
    args = parse_arguments()
    
    print(f"Generating synthetic market data:")
    print(f"- Days: {args.days}")
    print(f"- Interval: {args.interval} minute(s)")
    print(f"- Volatility: {args.volatility}")
    print(f"- Random seed: {args.seed}")
    
    # Generate data
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

if __name__ == "__main__":
    main()
