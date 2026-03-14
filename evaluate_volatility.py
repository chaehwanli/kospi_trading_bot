import sys
import os
import pandas as pd
import logging
from config import settings
from data.data_manager import DataManager

# Suppress Logs
logging.getLogger("DataManager").setLevel(logging.WARNING)

def evaluate_volatility():
    dm = DataManager(use_api=False) # Use already downloaded data
    
    results = []
    target_stocks = settings.TARGET_STOCKS
    
    print("Evaluating Volatility for Target Stocks...")
    
    for code in target_stocks:
        stock_name = settings.STOCK_NAMES.get(code, code)
        timeframe = settings.TIMEFRAME_MAP.get(code, "60")
        
        # Load data
        df = dm.load_data(code, time_unit=timeframe)
        if df is None or df.empty:
            continue
            
        try:
            # Ensure time is datetime for resampling
            df['datetime'] = pd.to_datetime(df['time'].astype(str))
            df.set_index('datetime', inplace=True)
            df.sort_index(inplace=True)
        except Exception as e:
            continue
            
        # Calculate Volatility Metrics
        # 1. 캔들 단위 변동성 (분봉 단위)
        df['range_pct'] = (df['high'] - df['low']) / df['low'] * 100
        avg_range_pct = df['range_pct'].mean()
        
        # 2. 수익률 표준편차 (기간별)
        df['return_pct'] = df['close'].pct_change() * 100
        volatility_std = df['return_pct'].std()
        
        # 3. 최대 낙폭 (Max Drawdown) - 대략적인 계산
        df['cummax'] = df['close'].cummax()
        df['drawdown'] = (df['close'] - df['cummax']) / df['cummax'] * 100
        max_drawdown = df['drawdown'].min()
        
        # 4. Weekly Volatility
        df_weekly = df.resample('W').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last'
        }).dropna()
        
        df_weekly['range_pct'] = (df_weekly['high'] - df_weekly['low']) / df_weekly['low'] * 100
        w_range_pct = df_weekly['range_pct'].mean()
        
        df_weekly['return_pct'] = df_weekly['close'].pct_change() * 100
        w_volatility_std = df_weekly['return_pct'].std()
        if pd.isna(w_volatility_std): w_volatility_std = 0
        
        # 5. Monthly Volatility
        resample_m = 'ME' if pd.__version__ >= '2.2.0' else 'M'
        try:
            df_monthly = df.resample(resample_m).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last'
            }).dropna()
        except:
            df_monthly = df.resample('M').agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last'
            }).dropna()
            
        df_monthly['range_pct'] = (df_monthly['high'] - df_monthly['low']) / df_monthly['low'] * 100
        m_range_pct = df_monthly['range_pct'].mean()
        
        df_monthly['return_pct'] = df_monthly['close'].pct_change() * 100
        m_volatility_std = df_monthly['return_pct'].std()
        if pd.isna(m_volatility_std): m_volatility_std = 0
        
        results.append({
            'code': code,
            'name': stock_name,
            'timeframe': f"{timeframe}M",
            'avg_candle_range': avg_range_pct,
            'volatility_std': volatility_std,
            'w_range_pct': w_range_pct,
            'w_volatility_std': w_volatility_std,
            'm_range_pct': m_range_pct,
            'm_volatility_std': m_volatility_std,
            'max_drawdown': max_drawdown
        })
        
    if not results:
        print("No downloaded data found. Please run 'python download_backtest_data.py' first.")
        return
        
    # Sort by Weekly Volatility (Standard Deviation of returns) - Descending
    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values('w_volatility_std', ascending=False)
    
    # Print Table
    print("\n[ 주간/월간 변동성 종합 평가 결과 (Volatility Analysis) ]")
    print(f"{'Code':<8} | {'Name':<12} | {'TF':<4} | {'Candle Dev':<10} | {'Weekly Dev':<10} | {'Monthly Dev':<11} | {'Max MDD(%)':<10}")
    print("-" * 80)
    
    for _, row in df_results.iterrows():
        print(f"{row['code']:<8} | {row['name']:<12} | {row['timeframe']:<4} | {row['volatility_std']:>10.2f} | {row['w_volatility_std']:>10.2f} | {row['m_volatility_std']:>11.2f} | {row['max_drawdown']:>10.2f}%")
        
    print("-" * 80)
    print("* Candle Dev: 기존 분봉 단위 수익률 표준편차")
    print("* Weekly Dev: 주 단위(Weekly) 수익률 표준편차")
    print("* Monthly Dev: 월 단위(Monthly) 수익률 표준편차")
    print("* Max MDD(%): 데이터 기간 중 최고점 대비 최대 하락폭")

if __name__ == "__main__":
    evaluate_volatility()
