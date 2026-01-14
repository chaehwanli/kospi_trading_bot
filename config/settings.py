import os
from dotenv import load_dotenv

load_dotenv()

# Account Settings
APP_KEY = os.getenv("APP_KEY", "")
APP_SECRET = os.getenv("APP_SECRET", "")
ACCOUNT_NO = os.getenv("ACCOUNT_NO", "") # Without hyphen usually, or as API expects
MODE = os.getenv("MODE", "PAPER") # PROD or PAPER

# URLs (Placeholder for Kiwoom REST API or KIS API)
# Note: Kiwoom standardly uses OCX on Windows. On Linux, this usually implies KIS (Korea Investment) or a bridge.
# Defaulting to KIS URLs as they are Linux-compatible and REST-based, assuming user might mean KIS or a Kiwoom Bridge.
URL_REAL = "https://openapi.koreainvestment.com:9443"
URL_PAPER = "https://openapivts.koreainvestment.com:29443"

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
