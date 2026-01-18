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

# Stock-Specific RSI Settings (Based on Optimization)
RSI_OVERSOLD_MAP = {
    "298380": 68, # ABL Bio (+180% at RSI 68)
    "084370": 60, # Eugene Tech (+137% at RSI 60)
    "007660": 58, # Isu Petasys (+80% at RSI 58)
    "056080": 60, # Eugene Robot (+78% at RSI 60)
    "014710": 48, # Sajo Seafood (+87% at RSI 48)
    "117730": 50, # T-Robotics (+77% at RSI 50)
    "336370": 50, # Solus (+64% at RSI 50)
    "358570": 42, # GI Innovation (+66% at RSI 42)
    "432720": 46  # Qualitas (+53% at RSI 46)
    # Others will fallback to RSI_OVERSOLD (50)
}

STOP_LOSS_PCT = -5.0  # -3.0%
TAKE_PROFIT_PCT = 12.0  # 35.0%
MAX_HOLD_DAYS = 5
STOP_LOSS_COOLDOWN_DAYS = 3
INITIAL_CAPITAL = 1000000  # 1 Million KRW
 
# RSI Optimization Defaults
RSI_OPTIMIZE_MIN = 30
RSI_OPTIMIZE_MAX = 70
RSI_OPTIMIZE_STEP = 2

# RSI Period Optimization Defaults
RSI_PERIOD_OPT_MIN = 3
RSI_PERIOD_OPT_MAX = 14
RSI_PERIOD_OPT_STEP = 1

# Stop Loss Optimization Defaults
STOP_LOSS_OPT_MIN = -5.0
STOP_LOSS_OPT_MAX = -1.0
STOP_LOSS_OPT_STEP = 0.5

# Take Profit Optimization Defaults
TAKE_PROFIT_OPT_MIN = 4.0
TAKE_PROFIT_OPT_MAX = 15.0
TAKE_PROFIT_OPT_STEP = 2.0

# Max Hold Days Optimization Defaults
MAX_HOLD_OPT_MIN = 1
MAX_HOLD_OPT_MAX = 5
MAX_HOLD_OPT_STEP = 1

# Target Stocks
# Sajo Seafood, Eugene Tech, Eugene Robot
TARGET_STOCKS = [
    "014710", # Sajo Seafood
    "084370", # Eugene Tech
    "056080", # Eugene Robot
    #"394280", # 오픈엣지테크놀로지
    #"108860", # 셀바스AI
    #"064290", # 인텍플러스
    "092870", # 엑시콘
    "117730", # 티로보틱스
    "432720", # 퀄리타스반도체
    #"396270", # 넥스트칩
    "358570", # 지아이이노베이션
    #"315640", # 딥노이드
    "402030", # 코난테크놀로지
    #"141080", # 리가켐바이오
    "237690", # ST팜
    "007660", # 이수페타시스
    #"328130", # 루닛
    "298380", # 에이비엘바이오
    #"052020", # 에스티큐브
    #"440110", # 파두
    "336370", # 솔루스첨단소재
    #"196170", # 알테오젠
    #"263050"  # 유틸렉스
]

STOCK_NAMES = {
    "014710": "사조씨푸드",
    "084370": "유진테크",
    "056080": "유진로봇",
    #"394280": "오픈엣지테크놀로지",
    #"108860": "셀바스AI",
    #"064290": "인텍플러스",
    "092870": "엑시콘",
    "117730": "티로보틱스",
    "432720": "퀄리타스반도체",
    #"396270": "넥스트칩",
    "358570": "지아이이노베이션",
    #"315640": "딥노이드",
    "402030": "코난테크놀로지",
    #"141080": "리가켐바이오",
    "237690": "ST팜",
    "007660": "이수페타시스",
    #"328130": "루닛",
    "298380": "에이비엘바이오",
    #"052020": "에스티큐브",
    #"440110": "파두",
    "336370": "솔루스첨단소재",
    #"196170": "알테오젠",
    #"263050": "유틸렉스"
}

# Reverse mapping for CLI
NAME_TO_CODE = {v: k for k, v in STOCK_NAMES.items()}

# Timeframes
TIMEFRAME = "1H" # 1 Hour

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
