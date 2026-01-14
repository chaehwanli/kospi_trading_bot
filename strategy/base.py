from abc import ABC, abstractmethod

class BaseStrategy(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def generate_signal(self, df):
        """
        Analyze the DataFrame and return a signal.
        df: pandas DataFrame with OHLCV data.
        Returns:
            dict with:
            'action': 'BUY' | 'SELL' | 'HOLD',
            'reason': str
        """
        pass
