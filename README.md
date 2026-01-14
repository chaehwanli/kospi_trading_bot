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

I have implemented the KOSPI trading bot as requested. The bot supports Backtesting and Real-time Trading using the Kiwoom (KIS) REST API.

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
```bash
python main.py data
```

### 3. Run Backtest
```bash
python main.py backtest
```

### 4. Run Bot
```bash
python main.py bot
```
