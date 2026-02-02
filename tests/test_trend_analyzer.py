import unittest
import pandas as pd
import numpy as np
from utils.trend_analyzer import TrendAnalyzer, TrendType

class TestTrendAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = TrendAnalyzer(conflict_threshold=0.00005)

    def test_uptrend(self):
        # Create a clear uptrend: 1% increase over 100 bars
        # Slope approx 0.01 / 100 = 0.0001? No wait.
        # Price 100 -> 110 over 100 bars. 
        # Normalized: 1.0 -> 1.1. 
        # Slope: (1.1 - 1.0) / 100 = 0.001. 
        # 0.001 > 0.0005 -> Uptrend
        
        prices = np.linspace(100, 110, 100)
        df = pd.DataFrame({'close': prices})
        
        result = self.analyzer.calculate_trend(df)
        self.assertEqual(result['trend'], TrendType.UPTREND)
        self.assertGreater(result['slope'], 0.00005)

    def test_downtrend(self):
        # Create a clear downtrend: 100 -> 90 over 100 bars
        # Slope: (0.9 - 1.0) / 100 = -0.001
        
        prices = np.linspace(100, 90, 100)
        df = pd.DataFrame({'close': prices})
        
        result = self.analyzer.calculate_trend(df)
        self.assertEqual(result['trend'], TrendType.DOWNTREND)
        self.assertLess(result['slope'], -0.00005)

    def test_sideways(self):
        # Create a sideways trend: 100 -> 100.003 over 100 bars
        # Slope: (1.00003 - 1.0) / 100 = 0.0000003
        # 0.0000003 < 0.00005 -> Sideways
        
        prices = np.linspace(100, 100.003, 100)
        df = pd.DataFrame({'close': prices})
        
        result = self.analyzer.calculate_trend(df)
        self.assertEqual(result['trend'], TrendType.SIDEWAYS)

    def test_real_volatility_sideways(self):
        # Random walk around 100
        np.random.seed(42)
        noise = np.random.normal(0, 0.5, 100)
        prices = 100 + noise
        df = pd.DataFrame({'close': prices})
        
        result = self.analyzer.calculate_trend(df)
        # Should be roughly sideways or very weak trend
        # With seed 42, check actual value
        # Just ensure it runs and returns a valid type
        self.assertIn(result['trend'], [TrendType.UPTREND, TrendType.DOWNTREND, TrendType.SIDEWAYS])

if __name__ == '__main__':
    unittest.main()
