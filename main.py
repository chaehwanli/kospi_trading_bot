import argparse
import sys
from config import settings
from utils.logger import setup_logger

logger = setup_logger("Main")

def run_data(code, days):
    # Force REAL Mode for Data Download
    import os
    settings.MODE = "REAL"
    settings.APP_KEY = os.getenv("APP_KEY_REAL", "")
    settings.APP_SECRET = os.getenv("APP_SECRET_REAL", "")
    # settings.ACCOUNT_NO might not be strictly needed for chart data but good practice
    settings.ACCOUNT_NO = os.getenv("ACCOUNT_NO_REAL", "")
    
    logger.info(f"Forced Real Mode for Data Download. MODE={settings.MODE}")

    from data.data_manager import DataManager
    dm = DataManager(use_api=True)
    if code:
        dm.fetch_and_save_data(code, period_days=days)
    else:
        for c in settings.TARGET_STOCKS:
            dm.fetch_and_save_data(c, period_days=days)

def run_backtest(code):
    from backtester.engine import BacktestEngine
    from strategy.rsi_macd import RsiMacdStrategy
    from data.data_manager import DataManager
    
    # Backtest does not need API
    dm = DataManager(use_api=False)
    strategy = RsiMacdStrategy()
    engine = BacktestEngine(strategy)
    
    codes = [code] if code else settings.TARGET_STOCKS
    
    for c in codes:
        logger.info(f"Running Backtest for {c}")
        df = dm.load_data(c)
        if df is None:
            logger.error(f"No data found for {c}. Run 'data' mode first.")
            continue
            
        engine.run(df)

def run_bot():
    from bot.trader import TradingBot
    bot = TradingBot()
    bot.start()

def main():
    parser = argparse.ArgumentParser(description="KOSPI Trading Bot")
    parser.add_argument("mode", choices=["bot", "backtest", "data"], help="Operation mode")
    parser.add_argument("--code", help="Stock code or Name (optional for data/backtest)")
    parser.add_argument("--name", help="Stock Code or Name (Available for backward compatibility)", dest="code_arg")
    parser.add_argument("--years", type=int, default=1, help="Number of years to fetch data for (default 1)")
    
    args = parser.parse_args()
    
    # Handle --code or the new argument logic. 
    # User might pass name in --code argument too.
    # Let's unify.
    
    target_code = args.code or args.code_arg
    
    if target_code:
        # Check if it's a name
        if target_code in settings.NAME_TO_CODE:
            target_code = settings.NAME_TO_CODE[target_code]
            logger.info(f"Resolved Name '{args.code or args.code_arg}' to Code '{target_code}'")
            
    if args.mode == "data":
        days = args.years * 365
        run_data(target_code, days)
    elif args.mode == "backtest":
        run_backtest(target_code)
    elif args.mode == "bot":
        run_bot()

if __name__ == "__main__":
    main()
