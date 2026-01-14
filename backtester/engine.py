import pandas as pd
from datetime import timedelta
from config import settings
from utils.logger import setup_logger

logger = setup_logger("Backtester")

class BacktestEngine:
    def __init__(self, strategy):
        self.strategy = strategy
        self.initial_capital = settings.INITIAL_CAPITAL
        self.balance = self.initial_capital
        self.position = None # { 'price': float, 'qty': int, 'time': datetime, 'cost': float }
        self.trades = []
        
        # Fees
        self.fee_buy = 0.00015 # 0.015%
        self.fee_sell = 0.00015 + 0.0018 # 0.015% + 0.18% Tax
        
    def run(self, df):
        """
        Run backtest on the provided DataFrame.
        """
        self.balance = self.initial_capital
        self.position = None
        self.trades = []
        
        logger.info(f"Starting Backtest. Initial Capital: {self.balance}")
        
        # We need to iterate row by row to simulate real-time
        # Use simple iteration for now
        
        # Pre-calculate indicators to speed up? 
        # Strategy calculates on the fly usually, but for backtest we can pass the whole DF if the strategy supports it.
        # But our strategy expects data up to point T.
        # RsiMacdStrategy.generate_signal computes on the whole df passed to it.
        # Passing growing window is slow.
        # Optimization: Calculate indicators once for the whole DF, then iterate.
        # I'll update Strategy to allow `precompute`? Or just trust pandas is fast enough for 1 year (1500 rows).
        # 1500 rows is tiny. Growing window is fine.
        
        # However, to be correct, indicators at time T should not know T+1.
        # `calculate_indicators` using `rolling` and `ewm` on the whole DF is correct 
        # because row T only depends on T-n..T.
        
        # So I will calculate indicators on the FULL DF once, then iterate.
        # I need to expose `calculate_indicators` in strategy or just use it.
        # Modifying strategy to return DataFrame with indicators.
        
        df_with_indicators = self.strategy.calculate_indicators(df.copy())
        
        for index, row in df_with_indicators.iterrows():
            current_time = row['time'] # assume string or datetime
            # Convert to datetime if str
            if isinstance(current_time, str):
                current_time = pd.to_datetime(current_time, format="%Y%m%d%H%M%S") # Format depends on API
                # API format: stck_bsop_date + stck_cntg_hour usually YYYYMMDDHHMMSS or similar
                # data_manager saves it as fetched.
            
            # 1. Manage Position
            if self.position:
                self._check_exit_conditions(row, current_time)
            
            # 2. Check Entry (if no position)
            # Re-check position because we might have just sold
            if not self.position:
                self._check_entry_conditions(row, index, df_with_indicators)
                
        # Finalize
        self._calculate_performance()
        
    def _check_exit_conditions(self, row, current_time):
        current_price = row['close']
        entry_price = self.position['price']
        
        # PnL %
        pnl_pct = (current_price - entry_price) / entry_price * 100
        
        # 1. Stop Loss
        if pnl_pct <= settings.STOP_LOSS_PCT: # -3.0
            self._sell(row, "Stop Loss")
            return

        # 2. Take Profit
        if pnl_pct >= settings.TAKE_PROFIT_PCT: # 35.0
            self._sell(row, "Take Profit")
            return
            
        # 3. Max Hold Days
        # Parse entry time
        entry_time = self.position['time']
        if isinstance(entry_time, str):
            entry_time = pd.to_datetime(entry_time) # robust check
            
        if (current_time - entry_time).days >= settings.MAX_HOLD_DAYS:
            self._sell(row, "Max Hold Reached")
            return
            
    def _check_entry_conditions(self, row, index, df):
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
        rsi_oversold = rsi < settings.RSI_OVERSOLD
        
        if macd_bullish and rsi_oversold:
            self._buy(row, "Strategy Signal")

    def _buy(self, row, reason):
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
            
            self.position = {
                'price': price,
                'qty': qty,
                'time': row['time'], # Keep original format or object
                'cost': cost,
                'fee_entry': fee
            }
            logger.info(f"BUY at {price} ({reason}) time={row['time']}")
            
    def _sell(self, row, reason):
        price = row['close']
        qty = self.position['qty']
        
        revenue = qty * price
        fee = revenue * self.fee_sell
        
        net_revenue = revenue - fee
        self.balance += net_revenue
        
        pnl = net_revenue - (self.position['cost'] + self.position['fee_entry'])
        pnl_pct = (pnl / (self.position['cost'] + self.position['fee_entry'])) * 100
        
        self.trades.append({
            'entry_time': self.position['time'],
            'exit_time': row['time'],
            'entry_price': self.position['price'],
            'exit_price': price,
            'qty': qty,
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'reason': reason
        })
        
        logger.info(f"SELL at {price} ({reason}) PnL: {pnl:.0f} ({pnl_pct:.2f}%)")
        self.position = None

    def _calculate_performance(self):
        final_balance = self.balance
        if self.position:
            # Mark to market current position
            # Simply ignore or cash out at last price?
            # Usually cash out for total equity calc.
            pass
            
        total_return = (final_balance - self.initial_capital) / self.initial_capital * 100
        logger.info(f"Backtest Finished.")
        logger.info(f"Initial: {self.initial_capital}")
        logger.info(f"Final: {final_balance:.0f}")
        logger.info(f"Return: {total_return:.2f}%")
        logger.info(f"Total Trades: {len(self.trades)}")
