
from main import run_data
from config import settings

if __name__ == "__main__":
    print(f"Starting data download for {len(settings.TARGET_STOCKS)} stocks...")
    print("Target Stocks:", [settings.STOCK_NAMES.get(c, c) for c in settings.TARGET_STOCKS])
    
    # Download 1 year of data (365 days)
    # This will fetch data from Real server even if in Paper mode (handled by run_data)
    run_data(None, 365)
    
    print("All downloads completed.")
