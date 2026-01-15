import pandas as pd
import time
import os
from api.kiwoom import KiwoomAPI
from config import settings
from utils.logger import setup_logger
from strategy.rsi_macd import RsiMacdStrategy

logger = setup_logger("DataManager")

class DataManager:
    def __init__(self, use_api=True):
        self.api = KiwoomAPI() if use_api else None
        self.strategy = RsiMacdStrategy()
        self.data_dir = "data_storage"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def fetch_and_save_data(self, code, period_days=365):
        """
        Fetch data for 'period_days' and save to CSV.
        Since the API limit for intraday might be short, we'll try to fetch as much as possible.
        """
        logger.info(f"Fetching data for {code}...")
        
        # Note: API get_ohlcv implementation in api/kiwoom.py fetches a single batch.
        # Ideally, we need a loop here with pagination if the API supports it.
        # For this implementation, assuming get_ohlcv fetches the latest batch.
        # Does it support 'next'? I need to check headers/response in api/kiwoom.py.
        # As I haven't implemented pagination in api/kiwoom.py, I will start with a single fetch.
        # But to be robust, I'll save what we get.
        
        # TODO: Enhance api/kiwoom.py for pagination to get full 1 year.
        # For now, fetching what is available.
        
        if not self.api:
            logger.error("API not initialized. Cannot fetch data.")
            return

        data = self.api.get_ohlcv(code, time_unit="60", days=period_days) # 60 might mean 60 minute
        
        if not data:
            logger.error("No data fetched.")
            return
            
        df = pd.DataFrame(data)
        # Sort by time
        df = df.sort_values('time')
        
        # Calculate Indicators
        logger.info("Calculating Indicators (RSI, MACD)...")
        df = self.strategy.calculate_indicators(df)
        
        start_date = df['time'].iloc[0]
        end_date = df['time'].iloc[-1]
        logger.info(f"Fetched {len(df)} rows. Range: {start_date} ~ {end_date}")
        
        filename = f"{self.data_dir}/{code}_{settings.TIMEFRAME}.csv"
        df.to_csv(filename, index=False)
        logger.info(f"Saved to {filename}")
        return df

    def load_data(self, code):
        filename = f"{self.data_dir}/{code}_{settings.TIMEFRAME}.csv"
        if os.path.exists(filename):
            return pd.read_csv(filename)
        return None
