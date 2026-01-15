import unittest
from datetime import datetime
from utils.market_time import get_trading_days_diff

class TestMarketTime(unittest.TestCase):
    def test_normal_days(self):
        # Mon to Tue (1 day)
        start = datetime(2025, 1, 6) # Mon
        end = datetime(2025, 1, 7)   # Tue
        self.assertEqual(get_trading_days_diff(start, end), 1)
        
    def test_weekend_days(self):
        # Fri to Mon (1 trading day)
        start = datetime(2025, 1, 10) # Fri
        end = datetime(2025, 1, 13)   # Mon
        self.assertEqual(get_trading_days_diff(start, end), 1)

    def test_holiday_exclusion(self):
        # 2025-01-27, 28, 29 are Lunar New Year (Mon, Tue, Wed)
        # Fri (24th) to Thu (30th)
        start = datetime(2025, 1, 24) # Fri
        end = datetime(2025, 1, 30)   # Thu (Next week)
        
        # Expected:
        # 24 (Fri) -> Start
        # 25 (Sat) -> Skip
        # 26 (Sun) -> Skip
        # 27 (Mon) -> Holiday Skip
        # 28 (Tue) -> Holiday Skip
        # 29 (Wed) -> Holiday Skip
        # 30 (Thu) -> Count (1)
        
        self.assertEqual(get_trading_days_diff(start, end), 1)
        
        # Verify 0 days if end falls on holiday?
        # If End is on Holiday (29 Wed), diff from Fri (24)?
        # 24 -> 29.
        # 25, 26, 27, 28, 29(Holiday).
        # Count = 0.
        end_holiday = datetime(2025, 1, 29)
        self.assertEqual(get_trading_days_diff(start, end_holiday), 0)

if __name__ == '__main__':
    unittest.main()
