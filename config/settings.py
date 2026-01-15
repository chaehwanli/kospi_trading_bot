import os
from dotenv import load_dotenv

load_dotenv()

# Account Settings
MODE = os.getenv("MODE", "PAPER") # PROD or PAPER

# Account Settings
if MODE == "PAPER":
    APP_KEY = os.getenv("APP_KEY_PAPER", "")
    APP_SECRET = os.getenv("APP_SECRET_PAPER", "")
    ACCOUNT_NO = os.getenv("ACCOUNT_NO_PAPER", "")
else:
    APP_KEY = os.getenv("APP_KEY_REAL", "")
    APP_SECRET = os.getenv("APP_SECRET_REAL", "")
    ACCOUNT_NO = os.getenv("ACCOUNT_NO_REAL", "")

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
 
# RSI Optimization Defaults
RSI_OPTIMIZE_MIN = 30
RSI_OPTIMIZE_MAX = 70
RSI_OPTIMIZE_STEP = 2

# Stop Loss Optimization Defaults
STOP_LOSS_OPT_MIN = -3.0
STOP_LOSS_OPT_MAX = -1.0
STOP_LOSS_OPT_STEP = 0.5

# Take Profit Optimization Defaults
TAKE_PROFIT_OPT_MIN = 10.0
TAKE_PROFIT_OPT_MAX = 35.0
TAKE_PROFIT_OPT_STEP = 5.0

# Max Hold Days Optimization Defaults
MAX_HOLD_OPT_MIN = 1
MAX_HOLD_OPT_MAX = 5
MAX_HOLD_OPT_STEP = 1

# Target Stocks
# Sajo Seafood, Eugene Tech, Eugene Robot
TARGET_STOCKS = [
    "014710", # Sajo Seafood
    "084370", # Eugene Tech
    "056080"  # Eugene Robot
]

STOCK_NAMES = {
    "014710": "사조씨푸드",
    "084370": "유진테크",
    "056080": "유진로봇"
}

# Reverse mapping for CLI
NAME_TO_CODE = {v: k for k, v in STOCK_NAMES.items()}

# Timeframes
TIMEFRAME = "1H" # 1 Hour

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
