import unittest
from utils.price_utils import get_tick_size

class TestPriceUtils(unittest.TestCase):
    def test_tick_ranges(self):
        # < 1,000
        self.assertEqual(get_tick_size(999), 1)
        self.assertEqual(get_tick_size(0), 1)
        
        # 1,000 ~ 5,000 (5 KRW)
        self.assertEqual(get_tick_size(1000), 5)
        self.assertEqual(get_tick_size(4999), 5)
        
        # 5,000 ~ 10,000 (10 KRW)
        self.assertEqual(get_tick_size(5000), 10)
        self.assertEqual(get_tick_size(9990), 10)
        
        # 10,000 ~ 50,000 (50 KRW)
        self.assertEqual(get_tick_size(10000), 50)
        self.assertEqual(get_tick_size(49950), 50)
        
        # 50,000 ~ 100,000 (100 KRW)
        self.assertEqual(get_tick_size(50000), 100)
        self.assertEqual(get_tick_size(99900), 100)
        
        # 100,000 ~ 500,000 (500 KRW)
        self.assertEqual(get_tick_size(100000), 500)
        self.assertEqual(get_tick_size(499500), 500)
        
        # >= 500,000 (1,000 KRW)
        self.assertEqual(get_tick_size(500000), 1000)
        self.assertEqual(get_tick_size(1000000), 1000)

    def test_tick_ranges_kosdaq(self):
        # KOSDAQ: 5,000 ~ 50,000 (Same)
        self.assertEqual(get_tick_size(5000, "KOSDAQ"), 10)
        self.assertEqual(get_tick_size(10000, "KOSDAQ"), 50)
        
        # KOSDAQ: >= 50,000 (Always 100)
        self.assertEqual(get_tick_size(50000, "KOSDAQ"), 100)
        self.assertEqual(get_tick_size(100000, "KOSDAQ"), 100)
        self.assertEqual(get_tick_size(500000, "KOSDAQ"), 100)
        self.assertEqual(get_tick_size(1000000, "KOSDAQ"), 100)

if __name__ == '__main__':
    unittest.main()
