from api.kiwoom import KiwoomAPI
from config import settings
import logging

# Setup Logger to Console
logger = logging.getLogger("KiwoomAPI")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

def test_30m():
    print("Initializing API...")
    api = KiwoomAPI()
    
    code = "005930" # Samsung Electronics
    print(f"Attempting to fetch 30M data for {code} (1 day only)...")
    
    # Try fetching just 1 day to minimize load
    data = api.get_ohlcv(code, time_unit="30", days=1)
    
    if data:
        print(f"Success! Fetched {len(data)} rows.")
        print(f"Sample: {data[0]}")
    else:
        print("Failed to fetch data.")

if __name__ == "__main__":
    test_30m()
