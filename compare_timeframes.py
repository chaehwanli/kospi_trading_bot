import sys
import os
import pandas as pd
import logging
from config import settings
from data.data_manager import DataManager
from backtester.engine import BacktestEngine
from strategy.rsi_macd import RsiMacdStrategy

# Suppress Logs
logging.getLogger("Backtester").setLevel(logging.WARNING)
logging.getLogger("DataManager").setLevel(logging.WARNING)
logging.getLogger("KiwoomAPI").setLevel(logging.WARNING)
logging.getLogger("Strategy").setLevel(logging.WARNING)

# 1. Override Settings to Scenario 2 (Minimum Profit Guarantee)
settings.STOP_LOSS_PCT = -5.0
settings.TAKE_PROFIT_PCT = 12.0
settings.MAX_HOLD_DAYS = 5
settings.MAX_HOLD_MAX_DAYS = 10
settings.MIN_PROFIT_YIELD = 3.0
settings.STOP_LOSS_COOLDOWN_DAYS = 3
settings.INITIAL_CAPITAL = 1000000

# 2. Define Stocks (Top Winners + Others from User List)
target_stocks = [
    "298380", # ABL Bio
    "084370", # Eugene Tech
    "014710", # Sajo Seafood
    "056080", # Eugene Robot
    "117730", # T-Robotics
    "005930", # Samsung Electronics
    "083650", # BHI
    "358570", # GI Innovation
    "007660", # Isu Petasys
    "336260", # Doosan Fuel Cell
    "432720", # Qualitas Semiconductor
    "034020", # Doosan Enerbility
    "247540", # Ecopro BM
    "089890", # Koses
    "336370", # Solus Advanced Materials
    "041830"  # InBody
]

def run_comparison():
    # 3. Initialize
    # use_api=True to allow fetching 30M data
    dm = DataManager(use_api=True)
    strategy = RsiMacdStrategy()
    engine = BacktestEngine(strategy)

    print(f"{'Code':<8} | {'Name':<12} | {'1H Ret':<8} | {'30M Ret':<8} | {'1H Trd':<6} | {'30M Trd':<6} | {'Diff':<7} | {'Diff(Trd)':<10}")
    print("-" * 100)

    for code in target_stocks:
        stock_name = settings.STOCK_NAMES.get(code, code)
        
        # --- 1H Backtest ---
        df_1h = dm.load_data(code, time_unit="60")
        if df_1h is None:
            # Fallback fetch
             df_1h = dm.fetch_and_save_data(code, time_unit="60")
             
        res_1h = engine.run(df_1h, code, save_results=False)
        
        # --- 30M Backtest ---
        # Try load first
        df_30m = dm.load_data(code, time_unit="30")
        if df_30m is None:
            # Fetch
            df_30m = dm.fetch_and_save_data(code, time_unit="30")

        if df_30m is None or df_30m.empty:
             print(f"{code:<8} | {stock_name:<12} | {res_1h['return']:>7.2f}% | {'N/A':>8} | {res_1h['total_trades']:<6} | {'N/A':<6}")
             continue

        res_30m = engine.run(df_30m, code, save_results=False)
        
        # Metrics
        ret_1h = res_1h['return']
        ret_30m = res_30m['return']
        diff = ret_30m - ret_1h
        
        trd_1h = res_1h['total_trades']
        trd_30m = res_30m['total_trades']
        diff_trd = trd_30m - trd_1h
        
        print(f"{code:<8} | {stock_name:<12} | {ret_1h:>7.2f}% | {ret_30m:>7.2f}% | {trd_1h:<6} | {trd_30m:<6} | {diff:>6.2f}% | {diff_trd:>+4}")
        
        import time
        time.sleep(1.0) # Avoid Rate Limit

    print("-" * 100)

if __name__ == "__main__":
    run_comparison()
