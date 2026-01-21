from backtester.engine import BacktestEngine
from strategy.rsi_macd import RsiMacdStrategy
from data.data_manager import DataManager

dm = DataManager(use_api=False)
df = dm.load_data("298380")
if df is None:
    print("No data loaded")
    exit()

engine = BacktestEngine(RsiMacdStrategy())
res = engine.run(df, "298380", save_results=False)

print(f"Total: {res['total_trades']}")
print(f"Win: {res['win_trades']}")
print(f"Loss: {res['loss_trades']}")
print(f"SL: {res['count_sl']}")
print(f"TP: {res['count_tp']}")
print(f"MH(W): {res['count_mh_win']}")
print(f"MH(L): {res['count_mh_loss']}")
