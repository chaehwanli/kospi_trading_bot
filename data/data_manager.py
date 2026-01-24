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
        # User requested to use REAL server for data fetching.
        # "PROD" mode uses real server.
        self.api = KiwoomAPI(mode="PROD") if use_api else None
        self.strategy = RsiMacdStrategy()
        self.data_dir = "data_storage"
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _get_filename(self, code, time_unit):
        # Map 60 to 1H for backward compatibility
        suffix = "1H" if str(time_unit) == "60" else f"{time_unit}M"
        return f"{self.data_dir}/{code}_{suffix}.csv"

    def fetch_and_save_data(self, code, period_days=365, time_unit="60"):
        """
        Fetch data for 'period_days' and save to CSV.
        """
        logger.info(f"Fetching {time_unit}M data for {code}...")
        
        if not self.api:
            logger.error("API not initialized. Cannot fetch data.")
            return
            
        # time_unit is passed directly (e.g., "60" or "30")
        data = self.api.get_ohlcv(code, time_unit=str(time_unit), days=period_days)
        
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
        
        filename = self._get_filename(code, time_unit)
        df.to_csv(filename, index=False)
        logger.info(f"Saved to {filename}")
        return df

    def load_data(self, code, time_unit="60"):
        filename = self._get_filename(code, time_unit)
        if os.path.exists(filename):
            return pd.read_csv(filename)
        return None
