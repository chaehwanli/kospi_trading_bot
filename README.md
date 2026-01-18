# kospi_trading_bot
국내 주식 종목 거래 봇, 키움증권

# 목적
KOSPI주식을 자동으로 매수 매도하는 봇을 구현한다.

# 증권사
키움증권을 사용한다.

# API
키움증권 REST API를 사용한다.

# 대상 시장
KOSPI 시장, 원화 거래

# BackTest
백테스트를 수행하는 로직 필요하다
전략을 백테스트로 검증한다
1. 시장에서 거래량이 많은 종목을 대상으로 백테스트후 수익이 나는 종목에 대해서 봇을 돌린다.
2. 백테스트는 1년간의 데이터를 사용한다.
3. 백테스트를 위한 데이터는 키움증권 REST API를 사용하고 백테스트를 위한 데이터를 저장한다.
4. 백테스트 후 최적의 RSI 값을 찾을수 있도록 최적화 명령이 필요하다.
5. 백테스트를 위한 데이터에는 RSI, MACD 가 필요하다.

# 종목
1. 예상 종목: 사조씨푸트, 유진테크, 유진로봇
2. 종목은 백테스트를 통해 결정한다.

# 전략
1. 정규장 시간동안 동작한다. 
2. 1시간 분봉을 확인한다.
3. 매수 시그널은 RSI + MACD 지표를 이용한다.
```
rsi_oversold = 50

        # MACD 골든크로스/데드크로스 확인
        macd_bullish = macd_line > signal_line and histogram > 0
        macd_bearish = macd_line < signal_line and histogram < 0
        
        # RSI 과매수/과매도 확인
        rsi_oversold = rsi < self.rsi_oversold
        rsi_overbought = rsi > (RSI_OVERBOUGHT - 10)
        rsi_neutral = self.rsi_oversold <= rsi <= (RSI_OVERBOUGHT - 10)

        # 매수 결정
        if macd_bullish and rsi_oversold:
            self.buy()
        else:
            self.nothing()
```
5. 손실/수익 
```
Stop Loss: -3.0%
Take Profit: 35.0%
Long Max Hold Days: 5일
```
6. 매도 규칙
6.1 손실/수익 구간을 지킨다. (Stop Loss, Take Profit)
6.2 최대 보유 기간을 지킨다. (Long Max Hold Days)
6.3 Stop Loss가 발생하면 매도후 CoolDown 을 3거래일동안 유지한다.

7. 거래 금액
초기 거래 시작 금액은 100만원으로 한다.
거래 수수료도 포함한다.
수익과 손실이 발생하면 초기 거래 금액에 계속 누적한다.

8. 거래 결과 알림
거래 결과를 텔레그램으로 알림한다.

9. 매수 판단 결과 알림
매수 판단 결과를 텔레그램으로 알림한다.

10. 국내 휴장일
국내 휴장일에 대해서는 거래하지 않는다.
토요일/일요일도 거래하지 않는다.
MAX HOLD DAYS 계산에 휴장일은 제외한다.

11. 거래 시간
정규장 시간동안 동작한다.

12. 슬리피지 고려
매수/매도 시 슬리피지가 발생할 수 있으므로 이를 고려한다.
국내장 거래는 10원 단위로 슬리피지를 적용한다. 매도 -10원, 매수 +10원
Backtest 시에도 적용한다.
거래시간도 슬리피지를 고려해서 정각 1분에 동작해. (예: 09:01에 1시간 봉 확인후 거래 여부 판단 동작)
```
국내 주식(KOSPI) 거래 단위(호가 단위)는 주가에 따라 다릅니다.

현재 한국거래소(KRX)의 호가 가격 단위는 다음과 같습니다:

1,000원 미만: 1원
1,000원 ~ 5,000원 미만: 5원
5,000원 ~ 10,000원 미만: 10원
10,000원 ~ 50,000원 미만: 50원
50,000원 ~ 100,000원 미만: 100원
100,000원 ~ 500,000원 미만: 500원
500,000원 이상: 1,000원
즉, 종목의 현재 가격에 따라 5원일 수도, 10원일 수도, 혹은 그 이상일 수도 있습니다.

저희 타겟 종목들의 대략적인 가격대(예: 유진로봇 5,000~10,000원 대)라면 10원이 맞을 수 있으나, 사조씨푸드(4,000원 대)의 경우 5원 단위입니다. 유진테크(30,000원 이상)는 50원 단위입니다.
```
가격대별 동적 호가 단위(Tick Size)를 적용한다.
주문 가능 수량은 수수료 포함하여 계좌 잔액 95%이내에서 결정한다.

13. 수수료 고려
매수/매도 시 수수료가 발생할 수 있으므로 이를 고려한다.
국내장 거래는 0.015%의 수수료를 적용한다.
Backtest 시에도 적용한다.

# KOSPI Trading Bot - Implementation Walkthrough

I have implemented the KOSPI trading bot as requested. The bot supports Backtesting and Real-time Trading using the Kiwoom REST API.

## Features Implemented
- **Strategy**: RSI (<50) + MACD (Golden Cross, Hist > 0) on 1-hour timeframe.
- **Risk Management**:
  - Stop Loss: -3.0%
  - Take Profit: +35.0%
  - Max Hold: 5 Days
- **Bot Engine**:
  - Real-time market hours check (09:00 - 15:30).
  - Hourly cycle execution.
  - Telegram integration for notifications.
  - State persistence (`bot_state.json`) to survive restarts.
- **Backtester**:
  - Simulates trading over historical CSV data.
  - Tracks Portfolio Value, Fees (0.015% + Tax), and PnL.
- **Data Management**:
  - Fetches and saves OHLCV data to CSV.

## Project Structure
- `api/kiwoom.py`: REST API Wrapper (Authentication, Quota, Order, Balance).
- `strategy/rsi_macd.py`: Signal logic implementation.
- `backtester/engine.py`: Backtesting logic.
- `bot/trader.py`: Live trading bot logic.
- `config/settings.py`: Configuration (Targets, Constants, API Keys).
- `main.py`: CLI Entry point.
- `make_plan.md`: The implementation plan (saved as requested).

## Verification
I have verified the strategy logic using unit tests:
```bash
python -m unittest tests/test_strategy.py
# Output: OK
```

## Usage
### 1. Configuration
This project uses a `.env` file for security. 
1. Open the `.env` file in the project root.
2. Fill in your `APP_KEY`, `APP_SECRET`, `ACCOUNT_NO` and Telegram details.

```bash
APP_KEY="your_actual_app_key"
APP_SECRET="your_actual_app_secret"
ACCOUNT_NO="12345678" # Your 8-10 digit account number
MODE="PAPER" # "PAPER" or "REAL"
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Fetch Data
You can fetch historical data for analysis or backtesting.
- The bot automatically calculates **RSI** and **MACD** indicators and saves them to the CSV.
- **Options**:
  - `--code`: Stock Node or Name (e.g. "014710", "사조씨푸드"). If omitted, fetches for all targets in settings.
  - `--years`: Data range in years (Default: **1**).

**Example**:
```bash
# Fetch 2 years of data for Sajo Seafood
python main.py data --code "사조씨푸드" --years 2

# [Batch] 실전/백테스트용 전체 종목 일괄 다운로드 (1년치)
python download_backtest_data.py
```

### 3. Run Backtest
백테스트를 실행하여 전략의 수익성을 검증할 수 있습니다.
* 주의: 백테스트 실행 시에는 API 연결을 하지 않고 로컬 데이터(`data_storage/`)만을 사용하므로, 먼저 `data` 모드를 통해 데이터를 수집해야 합니다.

**명령어**:
```bash
# 특정 종목(이름 또는 코드)에 대해 백테스트 실행
python main.py backtest --code "사조씨푸드"

# [Batch] 전체 타겟 종목 일괄 백테스트 및 수익률 정렬 출력
python batch_backtest.py
```

**실행 결과**:
백테스트 결과는 `backtest_results/` 디렉토리에 저장되며 두 가지 파일이 생성됩니다.

1. **요약 파일 (`summary_종목코드_시간.txt`)**:
전체 수익률 및 승률 정보를 포함합니다.
```
Backtest Result for 사조씨푸드(014710)
Date: 20260115_213213
Initial Capital: 1000000       # 초기 자본금 (원)
Final Balance: 1603513         # 최종 평가액 (보유 주식 포함)
Return: 60.35%                 # 총 수익률
Total Trades: 35               # 총 거래 횟수
Win Trades: 16                 # 수익 거래 횟수
Loss Trades: 19                # 손실 거래 횟수
Avg Profit: 90807              # 평균 수익금 (원)
Avg Loss: -44705               # 평균 손실금 (원)
```

2. **상세 거래 내역 (`trades_종목코드_시간.csv`)**:
각 거래별 진입/청산 시점과 수익/손실 내역을 기록합니다.
```csv
entry_time,exit_time,entry_price,exit_price,qty,pnl,pnl_pct,reason
2025-01-14 14:00:00,2025-01-20 09:00:00,4545.0,4445.0,219,-23947,-2.41,Max Hold Reached (LOSS)
2025-01-21 14:00:00,2025-01-24 09:00:00,4445.0,6100.0,219,359693,36.94,Take Profit
2025-01-31 15:00:00,2025-02-03 09:00:00,5680.0,5180.0,235,-120073,-8.99,Stop Loss
...
```
* **Reason**: 청산 사유 (`Take Profit`, `Stop Loss`, `Max Hold Reached (PROFIT/LOSS)`)

### 4. Run Optimization
전략의 수익률을 극대화하기 위해 두 가지 최적화 명령을 제공합니다.

#### 1) RSI Optimization (`rsi_optimize`)
`RSI` 과매도 기준값만을 변경하며 최적의 값을 찾습니다. 가장 빠르고 직관적입니다.

**명령어**:
```bash
# 기본 설정(settings.py)으로 실행
python main.py rsi_optimize --code "사조씨푸드"

# 범위 직접 지정 (예: 60~70, 2단위)
python main.py rsi_optimize --code "사조씨푸드" --min-rsi 60 --max-rsi 70 --step-rsi 2
```

#### 2) PnL & MaxHold Optimization (`pnl_maxhold_optimize`)
`Stop Loss`, `Take Profit`, `Max Hold Days` 3가지 변수를 조합하여 최적의 파라미터 셋을 찾습니다.
*   **변수**: Stop Loss (손절가), Take Profit (익절가), Max Hold Days (최대 보유일)
*   3가지 변수의 모든 조합을 테스트하므로 시간이 더 소요될 수 있습니다.

**명령어**:
```bash
# 기본 설정(settings.py)으로 실행
python main.py pnl_maxhold_optimize --code "사조씨푸드"

# 범위 직접 지정
python main.py pnl_maxhold_optimize --code "사조씨푸드" --min-sl -3.0 --max-sl -2.0 --step-sl 0.5 --min-tp 30 --max-tp 40 --step-tp 5

#### 3) RSI Period Optimization (`optimize_rsi_period.py`)
RSI 지표의 계산 기간(Period, 기본 14일)을 최적화합니다.

**명령어**:
```bash
# 기본 설정(settings.py의 RSI_PERIOD_OPT_*)으로 실행
python optimize_rsi_period.py --code "에이비엘바이오"

# 범위 직접 지정 (4~14, 2단위)
python optimize_rsi_period.py --code "014710" --min 4 --max 14 --step 2
```
```

**설정 (config/settings.py)**:
각 최적화 모드의 기본 탐색 범위를 설정할 수 있습니다.
```python
# RSI Defaults
RSI_OPTIMIZE_MIN = 30
RSI_OPTIMIZE_MAX = 70
RSI_OPTIMIZE_STEP = 2

# PnL & MaxHold Defaults
STOP_LOSS_OPT_MIN = -5.0
STOP_LOSS_OPT_MAX = -1.0
STOP_LOSS_OPT_STEP = 0.5

TAKE_PROFIT_OPT_MIN = 10.0
TAKE_PROFIT_OPT_MAX = 50.0
TAKE_PROFIT_OPT_STEP = 5.0

MAX_HOLD_OPT_MIN = 1
MAX_HOLD_OPT_MAX = 10
MAX_HOLD_OPT_STEP = 1
```

**실행 결과 예시 (PnL & MaxHold)**:
```
Optimization Results for 014710 - PnL & MaxHold (Top 10):
SL     | TP     | Hold | Return    | Trades | Win 
------------------------------------------------------------
-2.5   | 30.0   | 5    |  107.55%  | 38     | 17  
-2.5   | 40.0   | 5    |   90.85%  | 38     | 17  
...
Best: SL=-2.5, TP=30.0, Hold=5 (Return: 107.55%)
```

### 5. Run Bot
```bash
python main.py bot
```
## Holiday & Slippage Rules

I have implemented the holiday/weekend handling rules and the dynamic KOSPI tick size slippage.

### Holiday & Weekend Handling

#### 1. New Utility: `market_time.py`
Created `utils/market_time.py` with `get_trading_days_diff(start_date, end_date)`.
- Calculates the number of **trading days** between two dates.
- Excludes Weekends (Sat, Sun).
- Excludes Holidays defined in `config.holidays.MARKET_HOLIDAYS`.

#### 2. Trader & Backtester Update
Modified `bot/trader.py` and `backtester/engine.py` to use `get_trading_days_diff` for `MAX_HOLD_DAYS` checks.

### Slippage & Fee

#### 1. Fee (0.015%)
Verified that the 0.015% fee was already implemented in both the bot and backtester.

#### 2. Dynamic Tick Size (Slippage)
Implemented dynamic slippage based on KOSPI price ranges (e.g., 5 KRW, 10 KRW, 50 KRW depending on price).

- **New Utility**: `utils/price_utils.py` implemented `get_tick_size(price)`.
- **Trader (`bot/trader.py`)**:
  - `BUY`: Entry Price = Market Price + `get_tick_size(price)`
  - `SELL` / Exit Logic: Sell Price = Market Price - `get_tick_size(price)`
- **Backtester (`backtester/engine.py`)**:
  - Updated Buy/Sell logic to match the Trader's dynamic slippage.

### Verification

#### Unit Tests
- `tests/test_market_time.py`: Verified holiday/weekend exclusion logic.
- `tests/test_price_utils.py`: Verified tick size calculation for various price ranges (<1k, 1k-5k, 5k-10k, etc.).

**Test Output:**
```
Ran 1 test in 0.000s
OK
```

##
I have found some relevant GitHub repositories and Python packages for Kiwoom REST API usage:

kiwoom-restul (Python Wrapper)
Description: A simple wrapper for Kiwoom's RESTful API. Supports async requests.
Key Features: Abstraction of network protocols, Async/WebSocket support.
GitHub/PyPI: Search for kiwoom-restful on PyPI or GitHub.

kiwoom-rest-api (Python Client)
Description: Python client for accessing the Kiwoom REST API.
GitHub/PyPI: Search for kiwoom-rest-api.

Blog Resources:
There are some Korean blog posts (Tistory) detailing token issuance and OHLCV fetching using Python requests, which might be more direct if you want to avoid 3rd party wrappers.
