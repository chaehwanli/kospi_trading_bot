import pandas as pd
import os

# Update this path to the actual file generated in the previous step
csv_file = "backtest_results/trades_014710_20260115_213213.csv" 

if not os.path.exists(csv_file):
    print(f"File not found: {csv_file}")
    # Try finding the latest file
    files = sorted([f for f in os.listdir("backtest_results") if f.endswith(".csv")])
    if files:
        csv_file = os.path.join("backtest_results", files[-1])
        print(f"Using latest file: {csv_file}")
    else:
        exit(1)

df = pd.read_csv(csv_file)

total_pnl = df['pnl'].sum()
initial_capital = 1000000
calculated_final = initial_capital + total_pnl

print(f"Total PnL from CSV: {total_pnl}")
print(f"Calculated Final Balance: {calculated_final}")

# Check Averages
win_trades = df[df['pnl'] > 0]
loss_trades = df[df['pnl'] <= 0]

print(f"Win Count: {len(win_trades)}")
print(f"Loss Count: {len(loss_trades)}")
print(f"Avg Profit: {win_trades['pnl'].mean()}")
print(f"Avg Loss: {loss_trades['pnl'].mean()}")
