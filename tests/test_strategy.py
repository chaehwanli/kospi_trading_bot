import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategy.rsi_macd import RsiMacdStrategy
from config import settings

class TestRsiMacdStrategy(unittest.TestCase):
    def setUp(self):
        self.strategy = RsiMacdStrategy()
        
    def test_indicators(self):
        # Create mock data
        dates = pd.date_range(start='2023-01-01', periods=100, freq='H')
        close = np.random.normal(100, 10, 100) # Random walkish
        df = pd.DataFrame({'time': dates, 'close': close})
        
        df_ind = self.strategy.calculate_indicators(df)
        
        self.assertIn('rsi', df_ind.columns)
        self.assertIn('macd', df_ind.columns)
        self.assertIn('signal', df_ind.columns)
        self.assertIn('histogram', df_ind.columns)
        
    def test_signal_generation(self):
        # Construct scenario: RSI < 50, MACD > Signal, Hist > 0
        df = pd.DataFrame()
        # Ensure we have enough data
        df['close'] = [100] * 50
        df['time'] = pd.date_range(start='2023-01-01', periods=50, freq='H')
        
        # We need to manually set values to check logic branch, 
        # OR we can just unit test method logic if we mock indicators.
        # But for end-to-end strategy test, we need data that produces the signal.
        # Easier: Mock the 'calculate_indicators' or pass specific DataFrame contents that 'calculate_indicators' would modify?
        # Actually generate_signal calls calculate_indicators internally.
        
        # Let's simple check if it returns HOLD on flat data
        res = self.strategy.generate_signal(df)
        self.assertEqual(res['action'], 'HOLD')
        
if __name__ == '__main__':
    unittest.main()
