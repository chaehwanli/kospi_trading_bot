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

7. 거래 금액
초기 거래 시작 금액은 100만원으로 한다.
거래 수수료도 포함한다.
수익과 손실이 발생하면 초기 거래 금액에 계속 누적한다.

8. 거래 결과 알림
거래 결과를 텔레그램으로 알림한다.

9. 매수 판단 결과 알림
매수 판단 결과를 텔레그램으로 알림한다.

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
```

### 3. Run Backtest
백테스트를 실행하여 전략의 수익성을 검증할 수 있습니다.
* 주의: 백테스트 실행 시에는 API 연결을 하지 않고 로컬 데이터(`data_storage/`)만을 사용하므로, 먼저 `data` 모드를 통해 데이터를 수집해야 합니다.

**명령어**:
```bash
# 특정 종목(이름 또는 코드)에 대해 백테스트 실행
python main.py backtest --code "사조씨푸드"

# 전체 타켓 종목에 대해 실행
python main.py backtest
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

### 4. Run Optimization (RSI)
RSI 과매도 기준값(`RSI_OVERSOLD`)을 30~70 사이(설정 가능)로 변경해가며 백테스트를 반복 수행하여, 가장 높은 수익률을 기록하는 최적의 RSI 값을 찾습니다.

**명령어**:
```bash
# 기본 설정(settings.py)으로 최적화 실행
python main.py optimize --code "사조씨푸드"

# 범위 직접 지정 (예: 60~70, 2단위)
python main.py optimize --code "사조씨푸드" --min-rsi 60 --max-rsi 70 --step-rsi 2
```

**설정**:
기본 탐색 범위는 `config/settings.py`에서 변경할 수 있습니다.
```python
RSI_OPTIMIZE_MIN = 30
RSI_OPTIMIZE_MAX = 70
RSI_OPTIMIZE_STEP = 1
```

**실행 결과**:
수익률 상위 10개의 RSI 설정값과 결과를 출력합니다.
```
Optimization Results for 014710 (Top 10):
RSI   | Return     | Trades   | Win  
----------------------------------------
66    |  146.26%   | 56       | 30   
68    |  124.75%   | 57       | 29   
65    |  126.32%   | 55       | 28   
...
Best RSI: 66 (Return: 146.26%)
```

### 5. Run Bot
```bash
python main.py bot
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
