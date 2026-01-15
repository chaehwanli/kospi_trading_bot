import pandas as pd
import os
from datetime import datetime
from datetime import timedelta
from config import settings
from utils.logger import setup_logger

logger = setup_logger("Backtester")

class BacktestEngine:
    def __init__(self, strategy, rsi_oversold=None):
        self.strategy = strategy
        self.initial_capital = settings.INITIAL_CAPITAL
        self.balance = self.initial_capital
        self.position = None # { 'price': float, 'qty': int, 'time': datetime, 'cost': float }
        self.trades = []
        
        self.rsi_oversold = rsi_oversold if rsi_oversold is not None else settings.RSI_OVERSOLD
        
        # Fees
        self.fee_buy = 0.00015 # 0.015%
        self.fee_sell = 0.00015 + 0.0018 # 0.015% + 0.18% Tax
        
    def run(self, df, code="UNKNOWN", save_results=True):
        """
        Run backtest on the provided DataFrame.
        """
        self.balance = self.initial_capital
        self.save_results = save_results
        self.position = None
        self.trades = []
        self.start_date = None
        self.end_date = None
        self.code = code
        self.result_dir = "backtest_results"
        if not os.path.exists(self.result_dir):
            os.makedirs(self.result_dir)
        
        logger.info(f"Starting Backtest. Initial Capital: {self.balance}")
        
        # Pre-calculate indicators
        df_with_indicators = self.strategy.calculate_indicators(df.copy())
        
        last_row = None
        last_time = None
        
        for index, row in df_with_indicators.iterrows():
            last_row = row
            current_time = row['time'] # assume string or datetime
            
            # Ensure proper datetime conversion
            if not isinstance(current_time, pd.Timestamp):
                try:
                    str_time = str(int(float(current_time))) if not isinstance(current_time, str) else current_time
                    current_time = pd.to_datetime(str_time, format="%Y%m%d%H%M%S")
                except Exception as e:
                    logger.error(f"Failed to parse time {current_time}: {e}")
                    continue
            
            last_time = current_time
            if self.start_date is None:
                self.start_date = current_time
            self.end_date = current_time
            
            # 1. Manage Position
            if self.position:
                self._check_exit_conditions(row, current_time)
            
            # 2. Check Entry (if no position)
            if not self.position:
                self._check_entry_conditions(row, index, df_with_indicators, current_time)
                
        # Finalize - Force Close
        if self.position and last_row is not None:
            self._sell(last_row, "Backtest End", last_time)
            
        return self._calculate_performance()
        
    def _check_exit_conditions(self, row, current_time):
        current_price = row['close']
        entry_price = self.position['price']
        
        # PnL %
        pnl_pct = (current_price - entry_price) / entry_price * 100
        
        # 1. Stop Loss
        if pnl_pct <= settings.STOP_LOSS_PCT: # -3.0
            self._sell(row, "Stop Loss", current_time)
            return

        # 2. Take Profit
        if pnl_pct >= settings.TAKE_PROFIT_PCT: # 35.0
            self._sell(row, "Take Profit", current_time)
            return
            
        # 3. Max Hold Days
        # Parse entry time
        entry_time = self.position['time']
        if isinstance(entry_time, str):
            entry_time = pd.to_datetime(entry_time) # robust check
            
        if (current_time - entry_time).days >= settings.MAX_HOLD_DAYS:
            status = "PROFIT" if pnl_pct >= 0 else "LOSS"
            self._sell(row, f"Max Hold Reached ({status})", current_time)
            return
            
    def _check_entry_conditions(self, row, index, df, current_time):
        # We need to check if the Strategy signal fired.
        # Strategy `generate_signal` logic:
        # macd_bullish = (macd > signal) and (hist > 0)
        # rsi_oversold = rsi < threshold
        
        rsi = row['rsi']
        macd = row['macd']
        signal = row['signal']
        hist = row['histogram']
        
        # Check condition
        macd_bullish = (macd > signal) and (hist > 0)
        rsi_oversold = rsi < self.rsi_oversold
        
        if macd_bullish and rsi_oversold:
            self._buy(row, "Strategy Signal", current_time)

    def _buy(self, row, reason, current_time):
        price = row['close']
        max_buy_amt = self.balance
        
        # Calculate Qty
        # Cost = Qty * Price * (1 + fee)
        # Qty = Balance / (Price * (1 + fee))
        qty = int(max_buy_amt / (price * (1 + self.fee_buy)))
        
        if qty > 0:
            cost = qty * price
            fee = cost * self.fee_buy
            self.balance -= (cost + fee)
            logger.debug(f"Balance Update (BUY): {self.balance + (cost+fee)} -> {self.balance} (Cost: {cost}, Fee: {fee})")
            
            self.position = {
                'price': price,
                'qty': qty,
                'time': current_time, 
                'cost': cost,
                'fee_entry': fee
            }
            logger.info(f"BUY at {price} ({reason}) time={current_time}")
            
    def _sell(self, row, reason, current_time):
        price = row['close']
        qty = self.position['qty']
        
        revenue = qty * price
        fee = revenue * self.fee_sell
        
        net_revenue = revenue - fee
        self.balance += net_revenue
        logger.debug(f"Balance Update (SELL): {self.balance - net_revenue} -> {self.balance} (Rev: {revenue}, Fee: {fee})")
        
        pnl = net_revenue - (self.position['cost'] + self.position['fee_entry'])
        pnl_pct = (pnl / (self.position['cost'] + self.position['fee_entry'])) * 100
        
        self.trades.append({
            'entry_time': self.position['time'],
            'exit_time': current_time,
            'entry_price': self.position['price'],
            'exit_price': price,
            'qty': qty,
            'pnl': int(pnl),
            'pnl_pct': round(pnl_pct, 2),
            'reason': reason
        })
        
        logger.info(f"SELL at {price} ({reason}) PnL: {pnl:.0f} ({pnl_pct:.2f}%)")
        self.position = None

    def _calculate_performance(self):
        final_balance = self.balance
        # Position is guaranteed to be closed by run() logic
            
        total_return = (final_balance - self.initial_capital) / self.initial_capital * 100
        
        # Log to Console
        logger.info(f"Backtest Finished.")
        logger.info(f"Initial: {self.initial_capital}")
        logger.info(f"Final: {final_balance:.0f}")
        logger.info(f"Return: {total_return:.2f}%")
        logger.info(f"Total Trades: {len(self.trades)}")
        
        # Save Results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 1. Summary File
        summary_file = os.path.join(self.result_dir, f"summary_{self.code}_{timestamp}.txt")
        
        # Get Stock Name
        stock_name = settings.STOCK_NAMES.get(self.code, "Unknown")
        display_name = f"{stock_name}({self.code})"
        
        # Calculate Statistics
        win_trades = [t for t in self.trades if t['pnl'] > 0]
        loss_trades = [t for t in self.trades if t['pnl'] <= 0]
        
        win_count = len(win_trades)
        loss_count = len(loss_trades)
        
        avg_profit = sum(t['pnl'] for t in win_trades) / win_count if win_count > 0 else 0
        avg_loss = sum(t['pnl'] for t in loss_trades) / loss_count if loss_count > 0 else 0
        
        avg_profit = sum(t['pnl'] for t in win_trades) / win_count if win_count > 0 else 0
        avg_loss = sum(t['pnl'] for t in loss_trades) / loss_count if loss_count > 0 else 0
        
        if self.save_results:
            with open(summary_file, 'w') as f:
                f.write(f"Backtest Result for {display_name}\n")
                f.write(f"Period: {self.start_date} ~ {self.end_date}\n")
                f.write(f"Date: {timestamp}\n")
                f.write(f"Initial Capital: {self.initial_capital}\n")
                f.write(f"Final Balance: {final_balance:.0f}\n")
                f.write(f"Return: {total_return:.2f}%\n")
                f.write(f"Total Trades: {len(self.trades)}\n")
                f.write(f"Win Trades: {win_count}\n")
                f.write(f"Loss Trades: {loss_count}\n")
                f.write(f"Avg Profit: {int(avg_profit)}\n")
                f.write(f"Avg Loss: {int(avg_loss)}\n")
            logger.info(f"Summary saved to {summary_file}")
            
            # 2. Trades File
            if self.trades:
                trades_df = pd.DataFrame(self.trades)
                trades_file = os.path.join(self.result_dir, f"trades_{self.code}_{timestamp}.csv")
                trades_df.to_csv(trades_file, index=False)
                logger.info(f"Trades saved to {trades_file}")
                
        return {
            'final_balance': final_balance,
            'return': total_return,
            'total_trades': len(self.trades),
            'win_trades': win_count,
            'loss_trades': loss_count
        }
