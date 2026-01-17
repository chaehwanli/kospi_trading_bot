
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
        # Load data
        df = dm.load_data(c)
        if df is None:
            # Try reloading? Or just logging error
            logger.error(f"No data for {c}")
            continue
            
        # Run Backtest
        # save_results=False to avoid creating 23 csv files if user just wants summary?
        # User said "backtest 수행하고", usually implies full process.
        # But for 'batch' summary, maybe files are noise.
        # I'll enable it because "backtest" usually implies detailed logs are available if needed.
        # But to prevent spamming the console with engine logs, we might want to suppress them?
        # The Engine logs via 'Backtester' logger.
        res = engine.run(df, code=c, save_results=True)
        
        res['code'] = c
        res['name'] = settings.STOCK_NAMES.get(c, c)
        results.append(res)

    # Sort by success (Return)
    results.sort(key=lambda x: x['return'], reverse=True)
    
    # Print Table
    print("\n" + "="*115)
    print(f"{'Code':<8} | {'Name':<15} | {'Return':<9} | {'Trades':<6} | {'Win':<4} | {'SL':<4} | {'TP':<4} | {'MH(W)':<5} | {'MH(L)':<5}")
    print("-" * 115)
    
    for r in results:
         print(f"{r['code']:<8} | {r['name']:<15} | {r['return']:>7.2f}%  | {r['total_trades']:<6} | {r['win_trades']:<4} | {r['count_sl']:<4} | {r['count_tp']:<4} | {r['count_mh_win']:<5} | {r['count_mh_loss']:<5}")
    
    print("="*115 + "\n")

if __name__ == "__main__":
    run_batch_backtest()
