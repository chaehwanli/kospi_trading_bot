import sys
import os
import argparse
import pandas as pd
from config import settings
from data.data_manager import DataManager
from strategy.rsi_macd import RsiMacdStrategy
from backtester.engine import BacktestEngine
from utils.logger import setup_logger
from datetime import datetime

logger = setup_logger("RSI_Period_Validator")

def run_rsi_period_optimization(code, start_period, end_period, step):
    logger.info(f"Starting RSI Period Optimization for {code} (Range: {start_period}-{end_period}, Step: {step})")
    
    # 1. Load Data
    dm = DataManager(use_api=False) # Use local data
    df = dm.load_data(code)
    
    if df is None or df.empty:
        logger.error(f"No data found for {code}")
        return

    # 2. Iterate Periods
    results = []
    
    for period in range(start_period, end_period + 1, step):
        logger.info(f"Testing RSI Period: {period}")
        
        # Instantiate Strategy with specific Period
        strategy = RsiMacdStrategy(rsi_period=period)
        
        # Instantiate Engine
        # Engine will pick up RSI Threshold from Map (if exists) or Default
        engine = BacktestEngine(strategy)
        
        # Run Backtest
        res = engine.run(df, code, save_results=False)
        
        results.append({
            'period': period,
            'return': res['return'],
            'trades': res['total_trades'],
            'win': res['win_trades'],
            'sl': res['count_sl'],
            'tp': res['count_tp'],
            'mh_win': res['count_mh_win'],
            'mh_loss': res['count_mh_loss']
        })

    # 3. Sort Results (by Return desc)
    sorted_results = sorted(results, key=lambda x: x['return'], reverse=True)
    
    # 4. Display Summary
    print(f"\nOptimization Results for {code} - Target: RSI Period (Map Threshold Applied)")
    print(f"{'Period':<8} | {'Return':<10} | {'Trades':<8} | {'Win':<5} | {'SL':<4} | {'TP':<4} | {'MH(W)':<5} | {'MH(L)':<5}")
    print("-" * 80)
    for r in sorted_results:
        print(f"{r['period']:<8} | {r['return']:>9.2f}% | {r['trades']:<8} | {r['win']:<5} | {r['sl']:<4} | {r['tp']:<4} | {r['mh_win']:<5} | {r['mh_loss']:<5}")
    print("-" * 80)
    
    best_res = sorted_results[0]
    print(f"\nBest RSI Period: {best_res['period']} (Return: {best_res['return']:.2f}%)")
    
    # Save to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"backtest_results/optimization_rsi_period_{code}_{timestamp}.txt"
    with open(filename, 'w') as f:
        f.write(f"Optimization Results for {code} - RSI Period\n")
        f.write(f"{'Period':<8} | {'Return':<10} | {'Trades':<8} | {'Win':<5} | {'SL':<4} | {'TP':<4} | {'MH(W)':<5} | {'MH(L)':<5}\n")
        f.write("-" * 80 + "\n")
        for r in sorted_results:
            f.write(f"{r['period']:<8} | {r['return']:>9.2f}% | {r['trades']:<8} | {r['win']:<5} | {r['sl']:<4} | {r['tp']:<4} | {r['mh_win']:<5} | {r['mh_loss']:<5}\n")
        f.write("-" * 80 + "\n")
        f.write(f"\nBest RSI Period: {best_res['period']} (Return: {best_res['return']:.2f}%)\n")
    logger.info(f"Saved results to {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optimize RSI Period")
    parser.add_argument("--code", type=str, required=True, help="Stock Code")
    parser.add_argument("--min", type=int, default=settings.RSI_PERIOD_OPT_MIN, help="Min Period")
    parser.add_argument("--max", type=int, default=settings.RSI_PERIOD_OPT_MAX, help="Max Period")
    parser.add_argument("--step", type=int, default=settings.RSI_PERIOD_OPT_STEP, help="Step")
    
    args = parser.parse_args()
    
    code = args.code
    
    # Resolve Name to Code if necessary
    if code in settings.NAME_TO_CODE:
        start_code = code
        code = settings.NAME_TO_CODE[code]
        print(f"Resolved Stock Name '{start_code}' to Code: {code}")

    try:
        run_rsi_period_optimization(code, args.min, args.max, args.step)
    except KeyboardInterrupt:
        logger.info("Interrupted by user.")
    except Exception as e:
        logger.error(f"Error: {e}")
