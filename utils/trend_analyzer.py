import numpy as np
import pandas as pd
from enum import Enum

class TrendType(Enum):
    UPTREND = "UPTREND"
    DOWNTREND = "DOWNTREND"
    SIDEWAYS = "SIDEWAYS"

class TrendAnalyzer:
    def __init__(self, conflict_threshold=0.0005):
        """
        :param conflict_threshold: Slope threshold to decide localized trend vs sideways.
                                   Slope > threshold -> Uptrend
                                   Slope < -threshold -> Downtrend
                                   Otherwise -> Sideways
                                   Default 0.0005 means ~0.05% change per bar on average.
        """
        self.threshold = conflict_threshold

    def calculate_trend(self, df: pd.DataFrame, price_col='close') -> dict:
        """
        Calculates the trend of the given DataFrame based on Linear Regression of prices.
        
        Returns:
            {
                'trend': TrendType,
                'slope': float
            }
        """
        if df is None or len(df) < 2:
            return {'trend': TrendType.SIDEWAYS, 'slope': 0.0}

        prices = df[price_col].values
        
        # Normalize prices to start at 1.0 for comparable slope
        normalized_prices = prices / prices[0]
        
        x = np.arange(len(normalized_prices))
        slope, intercept = np.polyfit(x, normalized_prices, 1)
        
        if slope > self.threshold:
            trend = TrendType.UPTREND
        elif slope < -self.threshold:
            trend = TrendType.DOWNTREND
        else:
            trend = TrendType.SIDEWAYS
            
        return {
            'trend': trend,
            'slope': slope
        }
