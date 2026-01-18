import pandas as pd
import numpy as np
from strategy.base import BaseStrategy
from config import settings

class RsiMacdStrategy(BaseStrategy):
    def __init__(self, rsi_period=14):
        super().__init__()
        self.rsi_period = rsi_period
        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9
        
        self.rsi_oversold_threshold = settings.RSI_OVERSOLD

    def calculate_indicators(self, df):
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp12 = df['close'].ewm(span=self.macd_fast, adjust=False).mean()
        exp26 = df['close'].ewm(span=self.macd_slow, adjust=False).mean()
        df['macd'] = exp12 - exp26
        df['signal'] = df['macd'].ewm(span=self.macd_signal, adjust=False).mean()
        df['histogram'] = df['macd'] - df['signal']
        
        return df

    def generate_signal(self, df, rsi_oversold=None):
        if len(df) < self.macd_slow + self.macd_signal:
            return {'action': 'HOLD', 'reason': 'Not enough data'}
            
        df = self.calculate_indicators(df.copy())
        
        # Get latest row
        latest = df.iloc[-1]
        
        rsi = latest['rsi']
        macd_line = latest['macd']
        signal_line = latest['signal']
        histogram = latest['histogram']
        
        # Use provided RSI threshold or default
        threshold = rsi_oversold if rsi_oversold is not None else self.rsi_oversold_threshold
        
        macd_bullish = (macd_line > signal_line) and (histogram > 0)
        rsi_oversold_cond = rsi < threshold
        
        if macd_bullish and rsi_oversold_cond:
            return {
                'action': 'BUY',
                'reason': f"MACD Bullish (H:{histogram:.2f}) & RSI Oversold ({rsi:.2f} < {threshold})",
                'price': latest['close'],
                'time': latest['time']
            }
            
        return {'action': 'HOLD', 'reason': 'No Signal'}
