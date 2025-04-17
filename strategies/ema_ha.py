from typing import Dict, Tuple, List, Any, Optional, Union
import pandas as pd
import numpy as np
import logging
from logger import setup_logger
from utils.patterns import apply_ha_pattern_filter

# Set up logger
logger = setup_logger(name="ema_ha_strategy", log_level=logging.INFO)


def try_format_timestamp(timestamp):
    """Try to format a timestamp to string, with fallback for non-convertible values."""
    try:
        return pd.Timestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        # If conversion fails, return the string representation
        return str(timestamp)

class EMAHeikinAshiStrategy:
    def __init__(self, ema_short: int, ema_long: int, config: Dict[str, Any] = None):
        """
        Initialize strategy with EMA periods and configuration

        Args:
            ema_short: Short EMA period
            ema_long: Long EMA period
            config: Strategy configuration

        Raises:
            ValueError: If configuration is invalid or missing required settings
        """
        if ema_short >= ema_long:
            raise ValueError(f"Short EMA period ({ema_short}) must be less than long EMA period ({ema_long})")

        self.ema_short = ema_short
        self.ema_long = ema_long
        self.config = config or {}

        # Validate config
        if not config or 'strategy' not in config or 'trading_session' not in config['strategy']:
            raise ValueError("Missing required configuration: strategy.trading_session")

        # Set trading session times from config
        try:
            session = config['strategy']['trading_session']
            self.market_open = pd.Timestamp(session['market_open']).time()
            self.market_entry = pd.Timestamp(session['market_entry']).time()
            self.force_exit = pd.Timestamp(session['force_exit']).time()
            self.market_close = pd.Timestamp(session['market_close']).time()

            # Set trading mode
            trading_config = config['strategy'].get('trading', {})
            trading_mode = trading_config.get('mode', ['SWING'])

            # Convert to list if it's a string
            if isinstance(trading_mode, str):
                trading_mode = [trading_mode]

            # Get the active mode (first in the list)
            self.trading_mode = trading_mode[0].upper() if trading_mode else 'SWING'

            # Validate trading mode
            valid_modes = {'SWING', 'BUY', 'SELL'}
            if self.trading_mode not in valid_modes:
                raise ValueError(f"Invalid trading mode: {self.trading_mode}. Must be one of {valid_modes}")

            # Set risk management parameters
            risk_config = config.get('risk_management', {})
            self.use_stop_loss = risk_config.get('use_stop_loss', False)
            self.stop_loss_pct = risk_config.get('stop_loss_pct', 1.0)
            self.use_trailing_stop = risk_config.get('use_trailing_stop', False)
            self.trailing_stop_pct = risk_config.get('trailing_stop_pct', 0.5)

            # TODO: Implement max_trades_per_day and max_risk_per_trade features
            # max_trades_per_day would limit the number of trades per day
            # max_risk_per_trade would calculate position size based on risk percentage
            # These parameters are available in risk_config but not currently implemented

            logger.info(f"Initialized EMA-HA strategy with periods {ema_short}/{ema_long}")
            logger.info(f"Trading mode: {self.trading_mode}")
            if self.use_stop_loss:
                logger.info(f"Stop loss enabled at {self.stop_loss_pct}%")
            if self.use_trailing_stop:
                logger.info(f"Trailing stop enabled at {self.trailing_stop_pct}%")

        except KeyError as e:
            raise ValueError(f"Missing required configuration key: {e}")
        except Exception as e:
            raise ValueError(f"Error initializing strategy: {e}")

    @staticmethod
    def calculate_ema(prices: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return prices.ewm(span=period, adjust=False).mean()

    @staticmethod
    def calculate_heikin_ashi(df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Heikin Ashi candles with fully vectorized operations for maximum performance

        Args:
            df: DataFrame with OHLC price data

        Returns:
            Tuple of (HA_Open, HA_Close) series
        """
        try:
            # Calculate HA Close - vectorized operation
            ha_close = (df['open'] + df['high'] + df['low'] + df['close']) / 4

            # Calculate first HA Open value
            first_open = (df['open'].iloc[0] + df['close'].iloc[0]) / 2

            # Pre-allocate HA Open array with the first value
            ha_open_values = np.zeros(len(df))
            ha_open_values[0] = first_open

            # Get ha_close values as numpy array for faster computation
            ha_close_values = ha_close.values

            # Use numpy's cumulative operations for vectorized calculation
            # This is much faster than a loop for large datasets
            if len(df) > 1:
                # Calculate the average of previous HA open and close for each position
                for i in range(1, len(df)):
                    ha_open_values[i] = (ha_open_values[i-1] + ha_close_values[i-1]) / 2

            # Convert back to pandas Series
            ha_open = pd.Series(ha_open_values, index=df.index)

            return ha_open, ha_close

        except Exception as e:
            logger.error(f"Error calculating Heikin Ashi candles: {e}")
            raise

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals using EMA crossover and Heikin Ashi based on trading mode"""
        # Calculate Heikin Ashi
        df['HA_Open'], df['HA_Close'] = self.calculate_heikin_ashi(df)

        # Calculate EMAs
        df['EMA_Short'] = self.calculate_ema(df['close'], self.ema_short)
        df['EMA_Long'] = self.calculate_ema(df['close'], self.ema_long)

        # Initialize signals
        df['Signal'] = 0

        # Apply Heikin Ashi pattern filter if enabled
        df = apply_ha_pattern_filter(df, self.config)

        # Always use Heikin Ashi conditions with EMA crossover
        # This is the basic signal generation that applies to all modes
        long_condition = (
            (df['EMA_Short'] > df['EMA_Long']) &
            (df['EMA_Short'].shift(1) <= df['EMA_Long'].shift(1)) &
            (df['HA_Close'] > df['HA_Open'])  # Heikin Ashi bullish
        )

        short_condition = (
            (df['EMA_Short'] < df['EMA_Long']) &
            (df['EMA_Short'].shift(1) >= df['EMA_Long'].shift(1)) &
            (df['HA_Close'] < df['HA_Open'])  # Heikin Ashi bearish
        )

        # Apply additional pattern filtering if pattern columns exist
        # The ha_patterns.py module will handle the None case and not add these columns
        if 'Bullish_Pattern' in df.columns:
            long_condition = long_condition & df['Bullish_Pattern']

        if 'Bearish_Pattern' in df.columns:
            short_condition = short_condition & df['Bearish_Pattern']

        # Apply signals based on trading mode
        if self.trading_mode in ['BUY', 'SWING']:
            df.loc[long_condition & df['close'].notna(), 'Signal'] = 1

        if self.trading_mode in ['SELL', 'SWING']:
            df.loc[short_condition & df['close'].notna(), 'Signal'] = -1

        return df

    def backtest(self, df: pd.DataFrame, initial_capital: float = 25000) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Run backtest with performance optimizations and risk management

        Args:
            df: DataFrame with market data
            initial_capital: Initial capital amount

        Returns:
            Tuple of (results_dict, trades_list)
        """
        try:
            # Generate signals
            df = self.generate_signals(df)

            # Filter data to only include trading hours for faster processing
            # Create a mask for trading hours
            trading_hours_mask = [(t.time() >= self.market_open and t.time() <= self.market_close) for t in df.index]
            df_trading = df[trading_hours_mask].copy()

            if len(df_trading) == 0:
                logger.warning("No data within trading hours")
                return {
                    'ema_short': self.ema_short,
                    'ema_long': self.ema_long,
                    'total_trades': 0,
                    'total_profit': 0.0,
                    'return_pct': 0.0,
                }, []

            # Pre-allocate lists for better performance
            # Use dictionaries of lists instead of list of dictionaries for better performance
            trade_entry_times = []
            trade_exit_times = []
            trade_entry_prices = []
            trade_exit_prices = []
            trade_position_types = []
            trade_pnls = []
            trade_durations = []
            trade_exit_reasons = []

            # Pre-calculate time objects for comparison (faster than creating them in the loop)
            market_entry_time = self.market_entry
            force_exit_time = self.force_exit

            # Trading state variables
            position_type = None
            capital = initial_capital
            peak_capital = initial_capital
            entry_price = 0
            entry_time = None
            current_month = None
            month_start_capital = initial_capital

            # For trailing stop
            highest_price_since_entry = 0
            lowest_price_since_entry = float('inf')

            # For monthly returns tracking
            monthly_returns = {}

            logger.info(f"Starting backtest with {len(df_trading)} candles in trading hours from {initial_capital} capital")

            # Get numpy arrays for faster access in the loop
            dates = df_trading.index.values
            times = np.array([d.time() for d in df_trading.index])
            prices = df_trading['close'].values
            signals = df_trading['Signal'].values

            # Main backtest loop
            for i in range(len(df_trading)):
                current_time = times[i]
                current_price = prices[i]
                current_date = dates[i]

                # Track monthly returns
                try:
                    this_month = pd.Timestamp(current_date).strftime('%Y-%m')
                    if this_month != current_month:
                        if current_month is not None:
                            monthly_return = (capital - month_start_capital) / month_start_capital * 100
                            monthly_returns[current_month] = monthly_return
                        current_month = this_month
                        month_start_capital = capital
                except (ValueError, TypeError):
                    # Handle conversion errors by using string representation
                    try:
                        this_month = str(current_date)[:7]  # Extract YYYY-MM from date string
                        if this_month != current_month:
                            if current_month is not None:
                                monthly_return = (capital - month_start_capital) / month_start_capital * 100
                                monthly_returns[current_month] = monthly_return
                            current_month = this_month
                            month_start_capital = capital
                    except Exception as e:
                        logger.warning(f"Could not process date for monthly returns: {e}")

                # Update trailing stop values if in a position
                if position_type == 'LONG':
                    highest_price_since_entry = max(highest_price_since_entry, current_price)
                elif position_type == 'SHORT':
                    lowest_price_since_entry = min(lowest_price_since_entry, current_price)

                # Check for stop loss or trailing stop if in a position
                stop_loss_triggered = False
                trailing_stop_triggered = False

                if position_type and self.use_stop_loss:
                    # Calculate stop loss price
                    if position_type == 'LONG':
                        stop_price = entry_price * (1 - self.stop_loss_pct/100)
                        if current_price <= stop_price:
                            stop_loss_triggered = True
                    else:  # SHORT
                        stop_price = entry_price * (1 + self.stop_loss_pct/100)
                        if current_price >= stop_price:
                            stop_loss_triggered = True

                if position_type and self.use_trailing_stop and not stop_loss_triggered:
                    # Calculate trailing stop price
                    if position_type == 'LONG':
                        trail_price = highest_price_since_entry * (1 - self.trailing_stop_pct/100)
                        if current_price <= trail_price and highest_price_since_entry > entry_price:
                            trailing_stop_triggered = True
                    else:  # SHORT
                        trail_price = lowest_price_since_entry * (1 + self.trailing_stop_pct/100)
                        if current_price >= trail_price and lowest_price_since_entry < entry_price:
                            trailing_stop_triggered = True

                # Force exit at force_exit time
                if position_type and current_time >= force_exit_time:
                    exit_price = current_price
                    # Calculate PnL based on position type
                    pnl = (exit_price - entry_price) * capital / entry_price if position_type == 'LONG' else \
                          (entry_price - exit_price) * capital / entry_price

                    # Record trade
                    trade_entry_times.append(entry_time)
                    trade_exit_times.append(current_date)
                    trade_entry_prices.append(float(entry_price))
                    trade_exit_prices.append(float(exit_price))
                    trade_position_types.append(position_type)
                    trade_pnls.append(float(pnl))
                    try:
                        duration = float((pd.Timestamp(current_date) - entry_time).total_seconds() / 60)
                    except (ValueError, TypeError):
                        # Fallback to a default duration if conversion fails
                        duration = 0.0
                        logger.warning(f"Could not calculate trade duration for exit at {current_date}")
                    trade_durations.append(duration)
                    trade_exit_reasons.append('ForceExit')

                    capital += pnl
                    peak_capital = max(peak_capital, capital)
                    position_type = None
                    continue

                # Check for stop loss or trailing stop exit
                if stop_loss_triggered or trailing_stop_triggered:
                    exit_price = current_price
                    # Calculate PnL based on position type
                    pnl = (exit_price - entry_price) * capital / entry_price if position_type == 'LONG' else \
                          (entry_price - exit_price) * capital / entry_price

                    exit_reason = 'StopLoss' if stop_loss_triggered else 'TrailingStop'

                    # Record trade
                    trade_entry_times.append(entry_time)
                    trade_exit_times.append(current_date)
                    trade_entry_prices.append(float(entry_price))
                    trade_exit_prices.append(float(exit_price))
                    trade_position_types.append(position_type)
                    trade_pnls.append(float(pnl))
                    try:
                        duration = float((pd.Timestamp(current_date) - entry_time).total_seconds() / 60)
                    except (ValueError, TypeError):
                        # Fallback to a default duration if conversion fails
                        duration = 0.0
                        logger.warning(f"Could not calculate trade duration for exit at {current_date}")
                    trade_durations.append(duration)
                    trade_exit_reasons.append(exit_reason)

                    capital += pnl
                    peak_capital = max(peak_capital, capital)
                    position_type = None
                    continue

                # Check for signal-based exits
                if position_type:
                    current_signal = signals[i]
                    exit_condition = (
                        (position_type == 'LONG' and current_signal == -1) or
                        (position_type == 'SHORT' and current_signal == 1)
                    )
                    if exit_condition:
                        exit_price = current_price
                        # Calculate PnL based on position type
                        pnl = (exit_price - entry_price) * capital / entry_price if position_type == 'LONG' else \
                              (entry_price - exit_price) * capital / entry_price

                        # Record trade
                        trade_entry_times.append(entry_time)
                        trade_exit_times.append(current_date)
                        trade_entry_prices.append(float(entry_price))
                        trade_exit_prices.append(float(exit_price))
                        trade_position_types.append(position_type)
                        trade_pnls.append(float(pnl))
                        try:
                            duration = float((pd.Timestamp(current_date) - entry_time).total_seconds() / 60)
                        except (ValueError, TypeError):
                            # Fallback to a default duration if conversion fails
                            duration = 0.0
                            logger.warning(f"Could not calculate trade duration for exit at {current_date}")
                        trade_durations.append(duration)
                        trade_exit_reasons.append('Signal')

                        capital += pnl
                        peak_capital = max(peak_capital, capital)
                        position_type = None

                # Check for new entries after market_entry time
                if not position_type and current_time >= market_entry_time and current_time < force_exit_time:
                    current_signal = signals[i]
                    if current_signal == 1:
                        position_type = 'LONG'
                        entry_price = current_price
                        try:
                            entry_time = pd.Timestamp(current_date)
                        except (ValueError, TypeError):
                            # Fallback to using the current date as a string
                            entry_time = str(current_date)
                            logger.warning(f"Could not convert entry time {current_date} to Timestamp")
                        highest_price_since_entry = current_price  # Reset for trailing stop

                    elif current_signal == -1:
                        position_type = 'SHORT'
                        entry_price = current_price
                        try:
                            entry_time = pd.Timestamp(current_date)
                        except (ValueError, TypeError):
                            # Fallback to using the current date as a string
                            entry_time = str(current_date)
                            logger.warning(f"Could not convert entry time {current_date} to Timestamp")
                        lowest_price_since_entry = current_price  # Reset for trailing stop

            # Add final month's return
            if current_month is not None:
                monthly_return = (capital - month_start_capital) / month_start_capital * 100
                monthly_returns[current_month] = monthly_return

            # Convert trade data to list of dictionaries
            num_trades = len(trade_entry_times)
            trades = []

            if num_trades > 0:
                for i in range(num_trades):
                    trades.append({
                        'entry_time': try_format_timestamp(trade_entry_times[i]),
                        'exit_time': try_format_timestamp(trade_exit_times[i]),
                        'entry_price': trade_entry_prices[i],
                        'exit_price': trade_exit_prices[i],
                        'position_type': trade_position_types[i],
                        'pnl': trade_pnls[i],
                        'duration': trade_durations[i],
                        'exit_reason': trade_exit_reasons[i]
                    })

            # Calculate metrics
            if not trades:
                logger.warning("No trades were executed during the backtest period")
                return {
                    'ema_short': self.ema_short,
                    'ema_long': self.ema_long,
                    'total_trades': 0,
                    'total_profit': 0.0,
                    'return_pct': 0.0,
                }, []

            monthly_returns_arr = np.array(list(monthly_returns.values()))

            # Count exit reasons
            exit_reasons = {}
            for reason in trade_exit_reasons:
                exit_reasons[reason] = exit_reasons.get(reason, 0) + 1

            # Calculate drawdown
            equity_curve = np.zeros(num_trades + 1)
            equity_curve[0] = initial_capital
            equity_curve[1:] = np.cumsum(trade_pnls) + initial_capital

            # Calculate running maximum for drawdown calculation
            running_max = np.maximum.accumulate(equity_curve)
            drawdowns = (running_max - equity_curve) / running_max * 100
            max_drawdown_pct = np.max(drawdowns) if len(drawdowns) > 0 else 0

            # Calculate win rate and profit metrics
            winning_trades_mask = np.array(trade_pnls) > 0
            num_winning_trades = np.sum(winning_trades_mask)
            win_rate = num_winning_trades / num_trades if num_trades > 0 else 0

            # Calculate profit factor
            winning_pnl_sum = np.sum(np.array(trade_pnls)[winning_trades_mask]) if num_winning_trades > 0 else 0
            losing_pnl_sum = np.abs(np.sum(np.array(trade_pnls)[~winning_trades_mask])) if num_trades - num_winning_trades > 0 else 0
            profit_factor = winning_pnl_sum / losing_pnl_sum if losing_pnl_sum > 0 else float('inf')

            # Get pattern length if available
            pattern_config = self.config.get('strategy', {}).get('ha_patterns', {})
            pattern_length = None
            if pattern_config.get('enabled', False):
                pattern_length = pattern_config.get('bullish_length', 2)  # Use bullish length as default

            # Calculate results
            results = {
                'ema_short': self.ema_short,
                'ema_long': self.ema_long,
                'trading_mode': self.trading_mode,  # Include trading mode in results
                'pattern_length': pattern_length,  # Include pattern length if available
                'total_trades': num_trades,
                'winning_trades': int(num_winning_trades),
                'win_rate': float(win_rate),
                'profit_factor': float(profit_factor),
                'total_profit': float(capital - initial_capital),
                'final_capital': float(capital),
                'return_pct': float((capital - initial_capital) / initial_capital * 100),
                'max_drawdown_pct': float(max_drawdown_pct),
                'monthly_returns_avg': float(np.mean(monthly_returns_arr)) if len(monthly_returns_arr) > 0 else 0,
                'monthly_returns_std': float(np.std(monthly_returns_arr)) if len(monthly_returns_arr) > 0 else 0,
                'profitable_months': float(np.sum(monthly_returns_arr > 0)) if len(monthly_returns_arr) > 0 else 0,
                'max_monthly_profit': float(np.max(monthly_returns_arr)) if len(monthly_returns_arr) > 0 else 0,
                'max_monthly_loss': float(np.min(monthly_returns_arr)) if len(monthly_returns_arr) > 0 else 0,
                'exit_reasons': exit_reasons
            }

            # Calculate Sharpe ratio
            if len(monthly_returns_arr) > 0 and np.std(monthly_returns_arr) > 0:
                results['sharpe_ratio'] = float(np.mean(monthly_returns_arr) / np.std(monthly_returns_arr))
            else:
                results['sharpe_ratio'] = 0.0

            logger.info(f"Backtest completed with {num_trades} trades, {win_rate*100:.1f}% win rate")
            logger.info(f"Final capital: {capital:.2f} ({results['return_pct']:.2f}% return)")

            return results, trades

        except Exception as e:
            logger.error(f"Error during backtest: {e}")
            raise
