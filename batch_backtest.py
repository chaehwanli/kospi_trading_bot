
from config import settings
from backtester.engine import BacktestEngine
from strategy.rsi_macd import RsiMacdStrategy
from data.data_manager import DataManager
from utils.logger import setup_logger

# Disable excessive logging for cleaner output, or keep it?
# Let's use a separate logger
logger = setup_logger("BatchBacktest")

def run_batch_backtest():
    dm = DataManager(use_api=False)
    strategy = RsiMacdStrategy()
    engine = BacktestEngine(strategy)
    
    results = []
    
    print(f"Starting Batch Backtest for {len(settings.TARGET_STOCKS)} stocks...")
    
    for c in settings.TARGET_STOCKS:
        # Determine Timeframe
        timeframe = settings.TIMEFRAME_MAP.get(c, "60")
        
        # Load data
        df = dm.load_data(c, time_unit=timeframe)
        if df is None:
            # Try reloading? Or just logging error
            logger.error(f"No data for {c}")
            continue
            
        # Run Backtest
        res = engine.run(df, code=c, save_results=True)
        
        res['code'] = c
        res['name'] = settings.STOCK_NAMES.get(c, c)
        res['tf'] = "1H" if timeframe == "60" else f"{timeframe}M"
        results.append(res)

    # Sort by success (Return)
    results.sort(key=lambda x: x['return'], reverse=True)
    
    # Print Table
    print("\n" + "="*135)
    print(f"{'Code':<8} | {'Name':<15} | {'TF':<4} | {'Return':<9} | {'Trades':<6} | {'Win':<4} | {'Trend':<10} | {'SL':<4} | {'TP':<4} | {'MH(W)':<5} | {'MH(L)':<5} | {'Fees':<7}")
    print("-" * 145)
    
    for r in results:
         trend_str = r.get('trend', 'N/A')
         print(f"{r['code']:<8} | {r['name']:<15} | {r['tf']:<4} | {r['return']:>7.2f}%  | {r['total_trades']:<6} | {r['win_trades']:<4} | {trend_str:<10} | {r['count_sl']:<4} | {r['count_tp']:<4} | {r['count_mh_win']:<5} | {r['count_mh_loss']:<5} | {r['total_fees']:<7}")
    
    print("="*125 + "\n")

if __name__ == "__main__":
    run_batch_backtest()
