import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot.trader import TradingBot
from config import settings

class TestDynamicHolding(unittest.TestCase):
    def setUp(self):
        # Patch settings
        self.patcher = patch('bot.trader.settings')
        self.mock_settings = self.patcher.start()
        
        # Set default test values
        self.mock_settings.STOP_LOSS_PCT = -5.0
        self.mock_settings.TAKE_PROFIT_PCT = 12.0
        self.mock_settings.MAX_HOLD_DAYS = 5
        self.mock_settings.MAX_HOLD_MAX_DAYS = 10
        self.mock_settings.MIN_PROFIT_YIELD = 1.0
        self.mock_settings.TELEGRAM_BOT_TOKEN = "TEST"
        self.mock_settings.TELEGRAM_CHAT_ID = "TEST"
        self.mock_settings.TARGET_STOCKS = []
        self.mock_settings.STOCK_NAMES = {}
        self.mock_settings.MODE = "PAPER"
        
        # Initialize Bot with mocks
        with patch('bot.trader.KiwoomAPI'), patch('bot.trader.TelegramBot'), patch('bot.trader.setup_logger'):
            self.bot = TradingBot()
            
        # Mock execute_sell to track calls
        self.bot.execute_sell = MagicMock()
        
        # Dummy position data
        self.code = "005930"
        self.entry_price = 10000
        self.bot.positions = {
            self.code: {
                'price': self.entry_price,
                'qty': 10,
                'time': '2023-01-01T09:00:00'
            }
        }

    def tearDown(self):
        self.patcher.stop()

    def run_check_exit(self, days_held, current_price):
        # Mock get_trading_days_diff to return the desired days
        with patch('bot.trader.get_trading_days_diff', return_value=days_held):
            # Calculate current_price pnl for validation
            # pnl = (current_price - tick - entry) / entry
            # Ignoring tick size for simplicity in test setup, assuming test prices are clear enough
            # But trader.py does: sell_price = current_price - tick
            # We should mock get_tick_size to 0 for simpler math
            with patch('bot.trader.get_tick_size', return_value=0):
                self.bot.check_exit(self.code, current_price, datetime.now())

    def test_standard_exit_profit_met(self):
        """Case 1: 5 Days, 2.0% Profit (>= 1.0%) -> SELL"""
        days = 5
        price = 10200 # +2.0%
        
        self.run_check_exit(days, price)
        
        self.bot.execute_sell.assert_called_with(self.code, 10, price, "Max Hold (Profit Met 2.00%)")

    def test_extension_triggered(self):
        """Case 2: 5 Days, 0.5% Profit (< 1.0%) -> HOLD"""
        days = 5
        price = 10050 # +0.5%
        
        self.run_check_exit(days, price)
        
        self.bot.execute_sell.assert_not_called()

    def test_extension_continued(self):
        """Case 3: 7 Days, 0.8% Profit (< 1.0%) -> HOLD"""
        days = 7
        price = 10080 # +0.8%
        
        self.run_check_exit(days, price)
        
        self.bot.execute_sell.assert_not_called()

    def test_extension_success(self):
        """Case 4: 7 Days, 1.5% Profit (>= 1.0%) -> SELL"""
        days = 7
        price = 10150 # +1.5%
        
        self.run_check_exit(days, price)
        
        self.bot.execute_sell.assert_called_with(self.code, 10, price, "Max Hold (Profit Met 1.50%)")

    def test_hard_limit_force_exit(self):
        """Case 5: 10 Days, -2.0% Profit (Still < Min) -> SELL"""
        days = 10
        price = 9800 # -2.0%
        
        self.run_check_exit(days, price)
        
        self.bot.execute_sell.assert_called_with(self.code, 10, price, "Max Hold Limit Reached (10 days)")

    def test_stop_loss_precedence(self):
        """Case 6: 2 Days, -6.0% Profit (<= -5.0%) -> SELL (Stop Loss)"""
        days = 2
        price = 9400 # -6.0%
        
        self.run_check_exit(days, price)
        
        self.bot.execute_sell.assert_called_with(self.code, 10, price, "Stop Loss")

if __name__ == '__main__':
    unittest.main()
