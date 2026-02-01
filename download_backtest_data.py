from config import settings
import os
from data.data_manager import DataManager
from utils.logger import setup_logger

logger = setup_logger("BatchDownload")

if __name__ == "__main__":
    # Force settings to REAL for data download
    settings.MODE = "REAL"
    settings.APP_KEY = os.getenv("APP_KEY_REAL", "")
    settings.APP_SECRET = os.getenv("APP_SECRET_REAL", "")
    
    print(f"Starting BATCH data download for {len(settings.TARGET_STOCKS)} stocks...")
    print(f"Target Mode: {settings.MODE}")
    
    dm = DataManager(use_api=True)
    
    total = len(settings.TARGET_STOCKS)
    for i, code in enumerate(settings.TARGET_STOCKS):
        name = settings.STOCK_NAMES.get(code, "Unknown")
        print(f"[{i+1}/{total}] Processing {code} ({name})...")
        
        # 1. Download 1H (60m)
        dm.fetch_and_save_data(code, period_days=365, time_unit="60")
        
        # 2. Download 30M
        dm.fetch_and_save_data(code, period_days=365, time_unit="30")
        
    print("All downloads completed.")
