import argparse
import sys
import os
from datetime import datetime
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
        
def run_rsi_optimize(code, args):
    if not code:
        logger.error("RSI Optimization requires a specific --code argument.")
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
        
    results = [] # Initialize results list
    
    # RSI Optimization
    min_val, max_val, step_val = args.min_rsi, args.max_rsi, args.step_rsi
    logger.info(f"Starting RSI Optimization for {code} (Range: {min_val}-{max_val}, Step: {step_val})")
    
    for val in range(min_val, max_val + 1, step_val):
        strategy = RsiMacdStrategy()
        engine = BacktestEngine(strategy, rsi_oversold=val)
        res = engine.run(df, code=code, save_results=False)
        results.append({'param': val, 'return': res['return'], 'trades': res['total_trades'], 'win': res['win_trades']})

    # Sort by success (Return)
    results.sort(key=lambda x: x['return'], reverse=True)
    
    logger.info(f"\nOptimization Results for {code} - Target: RSI (Top 10):")
    logger.info(f"{'Param':<8} | {'Return':<10} | {'Trades':<8} | {'Win':<5}")
    logger.info("-" * 45)
    
    for r in results[:10]:
         logger.info(f"{r['param']:<8} | {r['return']:>7.2f}%  | {r['trades']:<8} | {r['win']:<5}")
         
    if results:
        best = results[0]
        logger.info("-" * 45)
        logger.info(f"Best RSI: {best['param']} (Return: {best['return']:.2f}%)")

def run_pnl_maxhold_optimize(code, args):
    if not code:
        logger.error("PnL & MaxHold Optimization requires a specific --code argument.")
        return

    from backtester.engine import BacktestEngine
    from strategy.rsi_macd import RsiMacdStrategy
    from data.data_manager import DataManager
    import numpy as np

    dm = DataManager(use_api=False)
    df = dm.load_data(code)
    
    if df is None:
        logger.error(f"No data found for {code}. Run 'data' mode first.")
        return
        
    logger.info(f"Starting PnL & MaxHold Optimization for {code}")
    
    # Ranges
    sl_vals = np.arange(args.min_sl, args.max_sl + (args.step_sl/1000), args.step_sl)
    tp_vals = np.arange(args.min_tp, args.max_tp + (args.step_tp/1000), args.step_tp)
    hold_vals = range(args.min_hold, args.max_hold + 1, args.step_hold)
    
    total_combinations = len(sl_vals) * len(tp_vals) * len(hold_vals)
    logger.info(f"Total Combinations to test: {total_combinations}")
    
    results = []
    
    count = 0
    for sl in sl_vals:
        for tp in tp_vals:
            for hold in hold_vals:
                sl = round(sl, 2)
                tp = round(tp, 2)
                
                strategy = RsiMacdStrategy()
                engine = BacktestEngine(strategy, stop_loss_pct=sl, take_profit_pct=tp, max_hold_days=hold)
                res = engine.run(df, code=code, save_results=False)
                
                results.append({
                    'sl': sl, 'tp': tp, 'hold': hold,
                    'return': res['return'],
                    'trades': res['total_trades'],
                    'win': res['win_trades']
                })
                count += 1
                if count % 100 == 0:
                    logger.debug(f"Progress: {count}/{total_combinations}")
                    
    # Sort by success (Return)
    results.sort(key=lambda x: x['return'], reverse=True)
    
    logger.info(f"\nOptimization Results for {code} - PnL & MaxHold (Top 50):")
    logger.info(f"{'SL':<6} | {'TP':<6} | {'Hold':<4} | {'Return':<9} | {'Trades':<6} | {'Win':<4}")
    logger.info("-" * 60)
    
    for r in results[:50]:
         logger.info(f"{r['sl']:<6} | {r['tp']:<6} | {r['hold']:<4} | {r['return']:>7.2f}%  | {r['trades']:<6} | {r['win']:<4}")
         
    if results:
        best = results[0]
        logger.info("-" * 60 + "\n")
        logger.info(f"Best: SL={best['sl']}, TP={best['tp']}, Hold={best['hold']} (Return: {best['return']:.2f}%)\n")
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_path = f"backtest_results/optimization_{code}_{timestamp}.txt"
        os.makedirs("backtest_results", exist_ok=True)
        
        with open(result_path, "w", encoding="utf-8") as f:
            f.write(f"Optimization Results for {code} - PnL & MaxHold\n")
            f.write(f"Date: {timestamp}\n")
            f.write(f"Total Combinations Tested: {total_combinations}\n")
            f.write("-" * 65 + "\n")
            f.write(f"{'SL':<6} | {'TP':<6} | {'Hold':<4} | {'Return':<9} | {'Trades':<6} | {'Win':<4}\n")
            f.write("-" * 65 + "\n")
            
            for r in results:
                f.write(f"{r['sl']:<6} | {r['tp']:<6} | {r['hold']:<4} | {r['return']:>7.2f}%  | {r['trades']:<6} | {r['win']:<4}\n")
            
            f.write("-" * 65 + "\n")
            f.write(f"Best: SL={best['sl']}, TP={best['tp']}, Hold={best['hold']} (Return: {best['return']:.2f}%)\n")
            
        logger.info(f"Full optimization results saved to {result_path}")

def run_bot():
    from bot.trader import TradingBot
    bot = TradingBot()
    bot.start()

def main():
    parser = argparse.ArgumentParser(description="KOSPI Trading Bot")
    parser.add_argument("mode", choices=["bot", "backtest", "data", "rsi_optimize", "pnl_maxhold_optimize"], help="Operation mode")
    parser.add_argument("--code", help="Stock code or Name (optional for data/backtest)")
    parser.add_argument("--name", help="Stock Code or Name (Available for backward compatibility)", dest="code_arg")
    parser.add_argument("--years", type=int, default=1, help="Number of years to fetch data for (default 1)")
    
    # RSI Optimization
    parser.add_argument("--min-rsi", type=int, default=settings.RSI_OPTIMIZE_MIN, help=f"Min RSI (default {settings.RSI_OPTIMIZE_MIN})")
    parser.add_argument("--max-rsi", type=int, default=settings.RSI_OPTIMIZE_MAX, help=f"Max RSI (default {settings.RSI_OPTIMIZE_MAX})")
    parser.add_argument("--step-rsi", type=int, default=settings.RSI_OPTIMIZE_STEP, help=f"Step RSI (default {settings.RSI_OPTIMIZE_STEP})")
    
    # PnL & MaxHold Optimization
    parser.add_argument("--min-sl", type=float, default=settings.STOP_LOSS_OPT_MIN, help=f"Min Stop Loss % (default {settings.STOP_LOSS_OPT_MIN})")
    parser.add_argument("--max-sl", type=float, default=settings.STOP_LOSS_OPT_MAX, help=f"Max Stop Loss % (default {settings.STOP_LOSS_OPT_MAX})")
    parser.add_argument("--step-sl", type=float, default=settings.STOP_LOSS_OPT_STEP, help=f"Step Stop Loss % (default {settings.STOP_LOSS_OPT_STEP})")
    
    parser.add_argument("--min-tp", type=float, default=settings.TAKE_PROFIT_OPT_MIN, help=f"Min Take Profit % (default {settings.TAKE_PROFIT_OPT_MIN})")
    parser.add_argument("--max-tp", type=float, default=settings.TAKE_PROFIT_OPT_MAX, help=f"Max Take Profit % (default {settings.TAKE_PROFIT_OPT_MAX})")
    parser.add_argument("--step-tp", type=float, default=settings.TAKE_PROFIT_OPT_STEP, help=f"Step Take Profit % (default {settings.TAKE_PROFIT_OPT_STEP})")
    
    parser.add_argument("--min-hold", type=int, default=settings.MAX_HOLD_OPT_MIN, help=f"Min Max Hold Days (default {settings.MAX_HOLD_OPT_MIN})")
    parser.add_argument("--max-hold", type=int, default=settings.MAX_HOLD_OPT_MAX, help=f"Max Max Hold Days (default {settings.MAX_HOLD_OPT_MAX})")
    parser.add_argument("--step-hold", type=int, default=settings.MAX_HOLD_OPT_STEP, help=f"Step Max Hold Days (default {settings.MAX_HOLD_OPT_STEP})")
    
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
    elif args.mode == "rsi_optimize":
        run_rsi_optimize(target_code, args)
    elif args.mode == "pnl_maxhold_optimize":
        run_pnl_maxhold_optimize(target_code, args)

if __name__ == "__main__":
    main()
