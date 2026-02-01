import os
from dotenv import load_dotenv

load_dotenv()

# Account Settings
MODE = os.getenv("MODE", "REAL") # REAL or PAPER

# Raw Keys (Exported for Cross-Mode Usage)
APP_KEY_PAPER = os.getenv("APP_KEY_PAPER", "")
APP_SECRET_PAPER = os.getenv("APP_SECRET_PAPER", "")
ACCOUNT_NO_PAPER = os.getenv("ACCOUNT_NO_PAPER", "")

APP_KEY_REAL = os.getenv("APP_KEY_REAL", "")
APP_SECRET_REAL = os.getenv("APP_SECRET_REAL", "")
ACCOUNT_NO_REAL = os.getenv("ACCOUNT_NO_REAL", "")

# Active Keys based on MODE
if MODE == "PAPER":
    APP_KEY = APP_KEY_PAPER
    APP_SECRET = APP_SECRET_PAPER
    ACCOUNT_NO = ACCOUNT_NO_PAPER
else:
    APP_KEY = APP_KEY_REAL
    APP_SECRET = APP_SECRET_REAL
    ACCOUNT_NO = ACCOUNT_NO_REAL

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
    "432720": 46,  # Qualitas (+53% at RSI 46)
    "074600": 64, # 원익QnC (+21% at RSI 50)
    "005930": 70 # Samsung (+21% at RSI 50)
    # Others will fallback to RSI_OVERSOLD (50)
}

STOP_LOSS_PCT = -5.0  # -3.0%
TAKE_PROFIT_PCT = 12.0  # 35.0%
MAX_HOLD_DAYS = 5
MAX_HOLD_MAX_DAYS = 10 # Hard Limit
MIN_PROFIT_YIELD = 3.0 # Minimum profit % required to exit at MAX_HOLD_DAYS
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

# Min Profit Optimization Defaults
MIN_PROFIT_OPT_MIN = 0.0
MIN_PROFIT_OPT_MAX = 4.0
MIN_PROFIT_OPT_STEP = 0.5

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
    #"263050", # 유틸렉스
    "041830", # 인바디
    "383220", # F&F
    "074600", # 원익QnC
    "027710", # 팜스토리
    "005930", # 삼성전자
    "006400", # 삼성SDI
    "373220", # LG에너지솔루션
    "126340", # 비나텍
    "083650", # 비에이치아이
    "034020", # 두산에너빌리티
    "336260", # 두산퓨얼셀
    "178320", # 서진시스템
    "416180", # 신성에스티
    "100840", # SNT에너지
    "107640", # 한중엔시에스
    "089890", # 코세스
    "365340", # 성일하이텍
    "267270", # HD현대건설기계
    "003670", # 포스코퓨처엠
    "247540", # 에코프로비엠
    "066970", # 엘앤에프
    "086520", # 에코프로
    "357580", # 아모센스
    "452280", # 한선엔지니어링
    "211270", # AP위성 (KOSDAQ)
    "307950", # 현대오토에버
    "457190", # 이수스페셜티케미컬
    "010130", # 고려아연
    "377300", # 카카오페이
    "000880", # 한화
    "086280", # 현대글로비스
    "042700", # 한미반도체
    # "006400", # 삼성SDI (Already included)
    "022100", # 포스코DX
    "005380", # 현대차
    "454910", # 두산로보틱스
    "000720", # 현대건설
    # "003670", # 포스코퓨처엠 (Already included)
    "052690", # 한전기술
    "402340", # SK스퀘어
    # "007660", # 이수페타시스 (Already included)
    "272210", # 한화시스템
    "012450", # 한화에어로스페이스
    "329180", # HD현대중공업
    "064400"  # LG씨엔에스
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
    #"263050": "유틸렉스",
    "041830": "인바디",
    "383220": "F&F",
    "074600": "원익QnC",
    "027710": "팜스토리",
    "005930": "삼성전자",
    "006400": "삼성SDI",
    "373220": "LG에너지솔루션",
    "126340": "비나텍",
    "083650": "비에이치아이",
    "034020": "두산에너빌리티",
    "336260": "두산퓨얼셀",
    "178320": "서진시스템",
    "416180": "신성에스티",
    "100840": "SNT에너지",
    "107640": "한중엔시에스",
    "089890": "코세스",
    "365340": "성일하이텍",
    "267270": "HD현대건설기계",
    "003670": "포스코퓨처엠",
    "247540": "에코프로비엠",
    "066970": "엘앤에프",
    "086520": "에코프로",
    "357580": "아모센스",
    "452280": "한선엔지니어링",
    "211270": "AP위성",
    "307950": "현대오토에버",
    "457190": "이수스페셜티케미컬",
    "010130": "고려아연",
    "377300": "카카오페이",
    "000880": "한화",
    "086280": "현대글로비스",
    "042700": "한미반도체",
    "022100": "포스코DX",
    "005380": "현대차",
    "454910": "두산로보틱스",
    "000720": "현대건설",
    "052690": "한전기술",
    "402340": "SK스퀘어",
    "272210": "한화시스템",
    "012450": "한화에어로스페이스",
    "329180": "HD현대중공업",
    "064400": "LG씨엔에스"
}

# Reverse mapping for CLI
NAME_TO_CODE = {v: k for k, v in STOCK_NAMES.items()}

# Timeframes
TIMEFRAME = "1H" # 1 Hour

# Stock-Specific Timeframe Settings (Hybrid Strategy)
# Default is TIMEFRAME (1H). Specific stocks use shorter timeframes.
TIMEFRAME_MAP = {
    "089890": "30", # Koses (1H: 45% -> 30M: 164%)
    "034020": "30", # Doosan Enerbility (1H: 46% -> 30M: 66%)
    "005930": "30", # Samsung Electronics (1H: 114% -> 30M: 121%)
    "432720": "30", # Qualitas Semiconductor (1H: 11% -> 30M: 14%)
    "006400": "30", # Samsung SDI (1H: -12% -> 30M: -1%)
    "373220": "30", # LG Energy Solution (1H: -5% -> 30M: 8%)
    "126340": "30", # VinaTech (1H: 22% -> 30M: 44%)
    "178320": "30", # Seojin System (1H: -20% -> 30M: -11%)
    "365340": "30", # SungEel HiTech (1H: 4% -> 30M: 14%)
    "003670": "30", # POSCO Future M (1H: 23% -> 30M: 28%)
    "066970": "30", # L&F (1H: 31% -> 30M: 56%)
    "452280": "30", # Hanseon Engineering (1H: -22% -> 30M: 21%)
    "211270": "30", # AP Satellite (1H: -0.8% -> 30M: 40%)
    "307950": "30", # Hyundai AutoEver (1H: -6% -> 30M: 74%)
    "457190": "30", # Isu Specialty Chemical (1H: -10% -> 30M: 27%)
    "010130": "30", # Korea Zinc (1H: -6% -> 30M: 42%)
    "005380": "30", # Hyundai Motor (1H: 13% -> 30M: 14%)
    "454910": "30", # Doosan Robotics (1H: -31% -> 30M: 12%)
    "000720": "30", # Hyundai E&C (1H: -17% -> 30M: 68%)
    "012450": "30", # Hanwha Aerospace (1H: 10% -> 30M: 32%)
    "329180": "30", # HD Hyundai Heavy Industries (1H: 10% -> 30M: 18%)
    "064400": "30"  # LG CNS (1H: -40% -> 30M: -13%)
}

# Market Type Map (Default: KOSPI)
MARKET_TYPE_MAP = {
    "211270": "KOSDAQ"
}

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
