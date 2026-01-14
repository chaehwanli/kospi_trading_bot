# Implementation Plan - KOSPI Trading Bot

## Goal Description
Build a KOSPI trading bot using Kiwoom Securities REST API. The bot will trade based on an RSI + MACD strategy on a 1-hour timeframe. It will include backtesting capabilities to verify the strategy on specific stocks (e.g., Sajo Seafood, Eugene Tech, Eugene Robot) before real trading.

## User Review Required
> [!IMPORTANT]
> - **Kiwoom API Access**: Ensure you have the necessary API keys (App Key, App Secret) and account number available for configuration.
> - **Telegram Token**: Need Telegram Bot Token and Chat ID for notifications.
> - **Virtual Env**: I will assume I can create/use a virtual environment if needed, or stick to standard python usage.

## Proposed Changes

### Configuration & Utils
#### [NEW] `config/settings.py`
- Store constants: API URLs, Account details (loaded from env), Trading parameters (Stop Loss, Take Profit, etc.).
#### [NEW] `utils/logger.py`
- Setup logging configuration.
#### [NEW] `utils/telegram_bot.py`
- Wrapper for Telegram notifications.

### API Layer
#### [NEW] `api/kiwoom.py`
- `KiwoomAPI` class.
- Methods: `get_token`, `get_ohlcv`, `get_balance`, `buy_order`, `sell_order`.
- Handle token lifecycle (access tokens expire).

### Data Layer
#### [NEW] `data/data_manager.py`
- Functions to fetch 1-year OHLCV data via `KiwoomAPI`.
- Save/Load data to/from CSV for backtesting.

### Strategy Layer
#### [NEW] `strategy/base.py`
- `BaseStrategy` abstract class.
#### [NEW] `strategy/rsi_macd.py`
- Inherits `BaseStrategy`.
- Implements the logic:
  - RSI oversold check (default < 50, but typically oversold is < 30, logic in prompt says `rsi_oversold = 50` and `rsi < self.rsi_oversold`, so we follow prompt: RSI < 50).
  - MACD Golden Cross (MACD > Signal & Hist > 0).
  - Generates BUY/SELL/HOLD signals.

### Backtest Layer
#### [NEW] `backtester/engine.py`
- Simulate trading over historical data.
- Track portfolio value (Start 1M KRW), fees, profit/loss.
- Enforce Stop Loss (-3.0%), Take Profit (+35.0%), Max Hold (5 days).

### Bot Layer
#### [NEW] `bot/trader.py`
- Main loop for real-time trading (during market hours).
- Scheduler to run checks every hour.
- Integration with Telegram for alerts.

### Entry Point
#### [NEW] `main.py`
- CLI to run backtest or start bot.

## Verification Plan

### Automated Tests
- I will create a simple test script `tests/test_strategy.py` to verify the signal logic with mock data.
- `tests/test_api_mock.py` to verify API wrapper structure (without real calls).

### Manual Verification
1. **Data Fetching**: Run `python main.py --mode data --code 014710` (Sajo Seafood) and check if CSV is created.
2. **Backtest**: Run `python main.py --mode backtest --code 014710` and inspect the output report.
3. **Paper Trading (Dry Run)**: Run `python main.py --mode trade --dry-run` to see if it logs buy signals correctly without sending real orders (if API supports or checking logs).
