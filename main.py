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
            
        engine.run(df, code=c)
        
def run_optimization(code, min_rsi=settings.RSI_OPTIMIZE_MIN, max_rsi=settings.RSI_OPTIMIZE_MAX, step_rsi=settings.RSI_OPTIMIZE_STEP):
    if not code:
        logger.error("Optimization requires a specific --code argument.")
        return

    from backtester.engine import BacktestEngine
    from strategy.rsi_macd import RsiMacdStrategy
    from data.data_manager import DataManager
    import pandas as pd

    dm = DataManager(use_api=False)
    df = dm.load_data(code)
    
    if df is None:
        logger.error(f"No data found for {code}. Run 'data' mode first.")
        return
        
    logger.info(f"Starting RSI Optimization for {code} (Range: {min_rsi}-{max_rsi}, Step: {step_rsi})")
    
    results = []
    
    # Iterate RSI Thresholds
    for rsi_val in range(min_rsi, max_rsi + 1, step_rsi): 
        strategy = RsiMacdStrategy()
        # Pass rsi_oversold to engine (override default)
        engine = BacktestEngine(strategy, rsi_oversold=rsi_val)
        
        # Run silently (no file save)
        res = engine.run(df, code=code, save_results=False)
        
        results.append({
            'rsi': rsi_val,
            'return': res['return'],
            'trades': res['total_trades'],
            'win': res['win_trades']
        })
        # logger.info(f"RSI {rsi_val}: Return {res['return']:.2f}%")
        
    # Sort by success (Return)
    results.sort(key=lambda x: x['return'], reverse=True)
    
    logger.info(f"\nOptimization Results for {code} (Top 10):")
    logger.info(f"{'RSI':<5} | {'Return':<10} | {'Trades':<8} | {'Win':<5}")
    logger.info("-" * 40)
    
    for r in results[:10]:
         logger.info(f"{r['rsi']:<5} | {r['return']:>7.2f}%  | {r['trades']:<8} | {r['win']:<5}")
         
    best = results[0]
    logger.info("-" * 40)
    logger.info(f"Best RSI: {best['rsi']} (Return: {best['return']:.2f}%)")

def run_bot():
    from bot.trader import TradingBot
    bot = TradingBot()
    bot.start()

def main():
    parser = argparse.ArgumentParser(description="KOSPI Trading Bot")
    parser.add_argument("mode", choices=["bot", "backtest", "data", "optimize"], help="Operation mode")
    parser.add_argument("--code", help="Stock code or Name (optional for data/backtest)")
    parser.add_argument("--name", help="Stock Code or Name (Available for backward compatibility)", dest="code_arg")
    parser.add_argument("--years", type=int, default=1, help="Number of years to fetch data for (default 1)")
    
    # Optimization Arguments
    parser.add_argument("--min-rsi", type=int, default=settings.RSI_OPTIMIZE_MIN, help=f"Minimum RSI threshold for optimization (default {settings.RSI_OPTIMIZE_MIN})")
    parser.add_argument("--max-rsi", type=int, default=settings.RSI_OPTIMIZE_MAX, help=f"Maximum RSI threshold for optimization (default {settings.RSI_OPTIMIZE_MAX})")
    parser.add_argument("--step-rsi", type=int, default=settings.RSI_OPTIMIZE_STEP, help=f"Step size for RSI optimization (default {settings.RSI_OPTIMIZE_STEP})")
    
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
    elif args.mode == "optimize":
        run_optimization(target_code, min_rsi=args.min_rsi, max_rsi=args.max_rsi, step_rsi=args.step_rsi)

if __name__ == "__main__":
    main()
