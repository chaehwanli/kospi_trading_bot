import argparse
import sys
from config import settings
from utils.logger import setup_logger

logger = setup_logger("Main")

def run_data(code):
    from data.data_manager import DataManager
    dm = DataManager()
    if code:
        dm.fetch_and_save_data(code)
    else:
        for c in settings.TARGET_STOCKS:
            dm.fetch_and_save_data(c)

def run_backtest(code):
    from backtester.engine import BacktestEngine
    from strategy.rsi_macd import RsiMacdStrategy
    from data.data_manager import DataManager
    
    dm = DataManager()
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
    parser.add_argument("--code", help="Stock code (optional for data/backtest)")
    
    args = parser.parse_args()
    
    if args.mode == "data":
        run_data(args.code)
    elif args.mode == "backtest":
        run_backtest(args.code)
    elif args.mode == "bot":
        run_bot()

if __name__ == "__main__":
    main()
