import unittest
from datetime import datetime, timedelta
from utils.market_time import get_trading_days_diff

class TestCooldown(unittest.TestCase):
    def test_cooldown_logic(self):
        # Scenario: Stop Loss happened on Friday (Day 0)
        # Cooldown = 3 days.
        # Should NOT trade on Monday (Day 1)
        # Should NOT trade on Tuesday (Day 2)
        # Should TRADE on Wednesday (Day 3) -> Diff >= 3

        # Assuming NO holidays for this specific test range to keep it simple,
        # or choosing a range known to be clear.
        # Let's use a clear range: Dec 1, 2025 (Mon) to Dec 5, 2025 (Fri)
        
        exit_time = datetime(2025, 12, 1, 10, 0, 0) # Monday
        
        # Tuesday (Day 1) - Blocked
        current_time = datetime(2025, 12, 2, 10, 0, 0)
        days_diff = get_trading_days_diff(exit_time, current_time)
        self.assertEqual(days_diff, 1)
        self.assertTrue(days_diff < 3) # BLOCKED
        
        # Wednesday (Day 2) - Blocked
        current_time = datetime(2025, 12, 3, 10, 0, 0)
        days_diff = get_trading_days_diff(exit_time, current_time)
        self.assertEqual(days_diff, 2)
        self.assertTrue(days_diff < 3) # BLOCKED
        
        # Thursday (Day 3) - Allowed
        current_time = datetime(2025, 12, 4, 10, 0, 0)
        days_diff = get_trading_days_diff(exit_time, current_time)
        self.assertEqual(days_diff, 3)
        self.assertFalse(days_diff < 3) # ALLOWED

    def test_cooldown_with_weekend(self):
        # Exit on Friday, Dec 5, 2025
        exit_time = datetime(2025, 12, 5, 10, 0, 0) # Friday
        
        # Monday (Dec 8) - Day 1
        current_time = datetime(2025, 12, 8, 10, 0, 0)
        days_diff = get_trading_days_diff(exit_time, current_time)
        self.assertEqual(days_diff, 1) 
        
        # Tuesday (Dec 9) - Day 2
        current_time = datetime(2025, 12, 9, 10, 0, 0)
        days_diff = get_trading_days_diff(exit_time, current_time)
        self.assertEqual(days_diff, 2)
        
        # Wednesday (Dec 10) - Day 3 (Allowed)
        current_time = datetime(2025, 12, 10, 10, 0, 0)
        days_diff = get_trading_days_diff(exit_time, current_time)
        self.assertEqual(days_diff, 3)

if __name__ == '__main__':
    unittest.main()
