import os
from dotenv import load_dotenv

load_dotenv()

# Account Settings
APP_KEY = os.getenv("APP_KEY", "")
APP_SECRET = os.getenv("APP_SECRET", "")
ACCOUNT_NO = os.getenv("ACCOUNT_NO", "") # Without hyphen usually, or as API expects
MODE = os.getenv("MODE", "PAPER") # PROD or PAPER

# Kiwoom REST API URLs
URL_REAL = "https://api.kiwoom.com"
URL_PAPER = "https://mockapi.kiwoom.com"

BASE_URL = URL_PAPER if MODE == "PAPER" else URL_REAL

# Trading Strategy Parameters
RSI_OVERSOLD = 50
STOP_LOSS_PCT = -3.0  # -3.0%
TAKE_PROFIT_PCT = 35.0  # 35.0%
MAX_HOLD_DAYS = 5
INITIAL_CAPITAL = 1000000  # 1 Million KRW

# Target Stocks
# Sajo Seafood, Eugene Tech, Eugene Robot
TARGET_STOCKS = [
    "014710", # Sajo Seafood
    "084370", # Eugene Tech
    "056080"  # Eugene Robot
]

# Timeframes
TIMEFRAME = "1H" # 1 Hour

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
