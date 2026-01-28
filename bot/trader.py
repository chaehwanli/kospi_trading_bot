import time
import json
import os
import pandas as pd
from datetime import datetime, timedelta
from api.kiwoom import KiwoomAPI
from strategy.rsi_macd import RsiMacdStrategy
from config import settings
from utils.logger import setup_logger
from utils.telegram_bot import TelegramBot
from config.holidays import MARKET_HOLIDAYS
from utils.market_time import get_trading_days_diff
from utils.price_utils import get_tick_size

logger = setup_logger("TradingBot")

class TradingBot:
    def __init__(self):
        self.api = KiwoomAPI()
        self.strategy = RsiMacdStrategy()
        self.telegram = TelegramBot(settings.TELEGRAM_BOT_TOKEN, settings.TELEGRAM_CHAT_ID)
        
        self.target_stocks = settings.TARGET_STOCKS
        self.state_file = "bot_state.json"
        
        # Load state: { code: { 'qty': int, 'price': float, 'time': str } }
        self.positions = self._load_state()

    def _get_msg_prefix(self, code):
        mode_str = "모의거래" if settings.MODE == "PAPER" else "실거래"
        broker = "키움증권"
        # Get Stock Name
        stock_name = settings.STOCK_NAMES.get(code, code)
        stock_display = f"{stock_name}({code})"
        return f"[{mode_str}/{broker}/{stock_display}]"

    def _load_state(self):
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    # Check if new format
                    if 'positions' in data:
                        self.last_exits = data.get('last_exits', {})
                        return data.get('positions', {})
                    else:
                        # Legacy format: data is positions
                        self.last_exits = {}
                        return data
            except Exception as e:
                logger.error(f"Failed to load state: {e}")
        self.last_exits = {}
        return {}

    def _save_state(self):
        state = {
            'positions': self.positions,
            'last_exits': self.last_exits
        }
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=4)

    def sync_state_with_account(self):
        """
        Synchronize local bot state with actual account holdings.
        Removes positions from local state if they don't exist in the account (Sold externally).
        """
        logger.info("Synchronizing Bot State with Real Account...")
        
        real_holdings = self.api.get_holdings()
        
        # Check for locally tracked positions that are no longer in account
        to_remove = []
        for code, pos in self.positions.items():
            if code not in real_holdings:
                logger.warning(f"Position {code} found in Bot State but NOT in Account. Assuming SOLD manually.")
                to_remove.append(code)
            else:
                # Update Qty if mismatch?
                # real_qty = real_holdings[code]
                # if real_qty != pos['qty']:
                #     logger.warning(f"Qty Mismatch for {code}: Bot={pos['qty']}, Real={real_qty}. Updating to Real.")
                #     self.positions[code]['qty'] = real_qty
                pass
                
        # Remove partial sells or fully closed
        for code in to_remove:
            del self.positions[code]
            
            # Should we add to last_exits?
            # We don't know the Reason or Price.
            # Just remove to prevent errors.
            
        if to_remove:
            self._save_state()
            logger.info(f"Removed {len(to_remove)} positions from local state.")
            
        logger.info("State Synchronization Complete.")

    def is_market_open(self):
        now = datetime.now()
        # Weekends
        if now.weekday() >= 5:
            return False
            
        # Holidays
        today_str = now.strftime("%Y-%m-%d")
        if today_str in MARKET_HOLIDAYS:
            return False
            
        # Time 09:00 ~ 15:30
        start = now.replace(hour=9, minute=0, second=0, microsecond=0)
        end = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return start <= now <= end

    def run_cycle(self):
        logger.info("Running trading cycle...")
        
        # Check Balance
        balance = self.api.get_balance()
        if balance is not None:
            logger.info(f"Current Deposit: {balance}")
        
        for code in self.target_stocks:
            try:
                self.process_stock(code, balance)
            except Exception as e:
                logger.error(f"Error processing {code}: {e}")
                self.telegram.send_message(f"Error processing {code}: {e}")

    def process_stock(self, code, balance):
        # Fetch Data
        # Determine Timeframe
        timeframe = settings.TIMEFRAME_MAP.get(code, "60") # Default to 60 (1H)
        
        # We need enough history for indicators (at least ~50-100 bars)
        # get_ohlcv implementation in api might need to return enough rows.
        # Assuming get_ohlcv returns latest 100 rows or so.
        data = self.api.get_ohlcv(code, timeframe)
        
        if not data:
            logger.warning(f"No data for {code} ({timeframe}M)")
            return
            
        df = pd.DataFrame(data)
        df = df.sort_values('time')
        # Get specific RSI for this stock
        rsi_oversold = settings.RSI_OVERSOLD_MAP.get(code, settings.RSI_OVERSOLD)
        
        # Check Strategy Signal
        signal_result = self.strategy.generate_signal(df, rsi_oversold=rsi_oversold)
        last_row = df.iloc[-1]
        current_price = last_row['close']
        current_time = datetime.now() # OR use API time
        
        # Check Position
        if code in self.positions:
            self.check_exit(code, current_price, current_time)
        else:
            if signal_result['action'] == 'BUY':
                # Check Cooldown
                skipped = False
                if code in self.last_exits:
                    last_exit = self.last_exits[code]
                    if "Stop Loss" in last_exit['reason']:
                        last_exit_time = datetime.fromisoformat(last_exit['time'])
                        current_time_dt = datetime.now() # Use current time for check
                        days_diff = get_trading_days_diff(last_exit_time, current_time_dt)
                        if days_diff < settings.STOP_LOSS_COOLDOWN_DAYS:
                            logger.info(f"Skipping Entry for {code} (Cooldown: {days_diff}/{settings.STOP_LOSS_COOLDOWN_DAYS} days)")
                            skipped = True
                
                if not skipped:
                    self.execute_buy(code, current_price, balance, signal_result['reason'])
            else:
                logger.info(f"{code}: No Signal ({signal_result['reason']})")

    def check_exit(self, code, current_price, current_time):
        pos = self.positions[code]
        entry_price = pos['price']
        entry_time_str = pos['time']
        # Parse Entry Time format depends on how we saved it. 
        # API returns YYYYMMDDHHMMSS usually.
        # Let's handle string parsing.
        
        # If saved as ISO string
        try:
            entry_time = datetime.fromisoformat(entry_time_str)
        except:
            # Fallback or assume YYYYMMDDHHMMSS
            # Simpler: just calculate days diff if we can parse.
            entry_time = datetime.now() # Fallback if parsing fails to avoid crash
        
        # Slippage: Sell at -Tick Size
        market_type = settings.MARKET_TYPE_MAP.get(code, "KOSPI")
        tick = get_tick_size(current_price, market_type)
        sell_price = current_price - tick
        pnl_pct = (sell_price - entry_price) / entry_price * 100
        
        reason = None
        days_held = get_trading_days_diff(entry_time, current_time)
        
        if pnl_pct <= settings.STOP_LOSS_PCT:
            reason = "Stop Loss"
        elif pnl_pct >= settings.TAKE_PROFIT_PCT:
            reason = "Take Profit"
        elif days_held >= settings.MAX_HOLD_MAX_DAYS:
            reason = f"Max Hold Limit Reached ({days_held} days)"
        elif days_held >= settings.MAX_HOLD_DAYS:
            if pnl_pct >= settings.MIN_PROFIT_YIELD:
                reason = f"Max Hold (Profit Met {pnl_pct:.2f}%)"
            else:
                # Extending holding
                logger.debug(f"{code} holding extended: {days_held} days, PnL {pnl_pct:.2f}% < {settings.MIN_PROFIT_YIELD}%")

            
        if reason:
            self.execute_sell(code, pos['qty'], current_price, reason)

    def execute_buy(self, code, price, balance, reason):
        # Calculate Qty
        # Allocate portion of capital? Or all in?
        # "초기 거래 시작 금액은 100만원... 수익과 손실이 발생하면 계속 누적"
        # If we trade multiple stocks, how to split?
        # Assumption: We split capital or use available.
        # If we have 3 stocks, maybe 1/3 each? Or use all available?
        # Prompt doesn't specify splitting. 
        # But if we buy one, we might use all cash.
        # Let's be safe and use 1/N of Total Balance or just 100% if only one trade active?
        # Let's assume sequential: Use available cash.
        
        # Fee buffer
        if not balance:
            logger.error("Balance unknown, cannot buy.")
            return

        invest_amount = balance * 0.95 # Use 95% of available (Buffer for slippage/fees)
        # Or maybe limit to 1/len(target_stocks)?
        # Let's use full for simplicity as per "100만원... 누적" which implies single pot.
        
        if invest_amount < 10000: # Min amount check
            return
            
        fee_rate = 0.00015
        # Slippage: Buy at +Tick Size
        market_type = settings.MARKET_TYPE_MAP.get(code, "KOSPI")
        tick = get_tick_size(price, market_type)
        buy_price = price + tick
        qty = int(invest_amount / (buy_price * (1 + fee_rate)))
        
        if qty > 0:
            res = self.api.place_order(code, qty, "BUY", 0) # Market Order
            if res:
                self.positions[code] = {
                    'price': buy_price,
                    'qty': qty,
                    'time': datetime.now().isoformat()
                }
                self._save_state()
                import locale
                prefix = self._get_msg_prefix(code)
                msg = f"{prefix} BUY: {qty}주 @ {price} ({reason})"
                logger.info(msg)
                self.telegram.send_message(msg)

    def execute_sell(self, code, qty, price, reason):
        res = self.api.place_order(code, qty, "SELL", 0) # Market Order
        if res:
            market_type = settings.MARKET_TYPE_MAP.get(code, "KOSPI")
            tick = get_tick_size(price, market_type)
            sell_price = price - tick
            pnl_pct = (sell_price - self.positions[code]['price']) / self.positions[code]['price'] * 100
            prefix = self._get_msg_prefix(code)
            msg = f"{prefix} SELL: {qty}주 @ {price} ({reason}) PnL: {pnl_pct:.2f}%"
            logger.info(msg)
            self.telegram.send_message(msg)
            
            # Record Exit for Cooldown
            self.last_exits[code] = {
                'time': datetime.now().isoformat(),
                'reason': reason
            }
            
            del self.positions[code]
            self._save_state()

    def start(self):
        logger.info("Bot Started.")
        self.telegram.send_message("KOSPI Trading Bot Started.")
        
        # Synchronize State
        try:
            self.sync_state_with_account()
        except Exception as e:
            logger.error(f"State Sync Failed: {e}")
            self.telegram.send_message(f"⚠️ State Sync Failed: {e}")
        
        last_run_hour = -1
        
        while True:
            try:
                now = datetime.now()
                
                # Check Market Open (Day/Time)
                if self.is_market_open():
                    # Run logic at Minute 01
                    if now.minute == 1:
                        if now.hour != last_run_hour:
                            logger.info(f"Scheduled Run at {now.strftime('%H:%M')}")
                            self.run_cycle()
                            last_run_hour = now.hour
                            # Sleep to avoid double run within the same minute? 
                            # No, next loop iteration minute might still be 1 if run_cycle was fast.
                            # But last_run_hour check prevents it.
                    else:
                        # Reset last_run_hour if minute is NOT 1 (optional, but good for safety if restarted)
                        # Actually strict `!= last_run_hour` is enough. 
                        # But what if we restart at 09:01? last_run_hour=-1 -> Runs immediately. Correct.
                        pass
                else:
                    if now.minute == 0: # Log once an hour when closed
                        logger.info("Market Closed. Waiting...")
                
                # Sleep 10 seconds to ensure we catch the minute 01
                time.sleep(10)
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Loop Error: {e}")
                time.sleep(60)
