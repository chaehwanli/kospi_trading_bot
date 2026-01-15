from datetime import timedelta
from config.holidays import MARKET_HOLIDAYS

def get_trading_days_diff(start_date, end_date):
    """
    Calculate the number of trading days between start_date and end_date.
    Excludes weekends (Sat, Sun) and holidays defined in MARKET_HOLIDAYS.
    start_date is excluded, end_date is included. 
    (Similar to standard logic: day 1 to day 2 is 1 day difference if day 2 is trading day)
    
    Actually, for "Holding Days", if I buy on Monday (Day 1) and sell on Tuesday (Day 2), held for 1 day.
    To be robust: we count business days.
    
    If start_date == end_date, diff is 0.
    """
    if start_date.date() >= end_date.date():
        return 0
        
    current_date = start_date.date()
    end_date_val = end_date.date()
    
    trading_days = 0
    
    # Iterate from start_date + 1 day until end_date (inclusive)
    # We want to count how many trading days have passed.
    
    # Example: Buy Mon, Current Tue.
    # Check Tue. Trade Day? Yes. Count = 1.
    
    # Example: Buy Fri, Current Mon.
    # Check Sat (Skip), Sun (Skip), Mon (Yes). Count = 1.
    
    while current_date < end_date_val:
        current_date += timedelta(days=1)
        
        # Check Weekend (5=Sat, 6=Sun)
        if current_date.weekday() >= 5:
            continue
            
        # Check Holiday
        date_str = current_date.strftime("%Y-%m-%d")
        if date_str in MARKET_HOLIDAYS:
            continue
            
        trading_days += 1
        
    return trading_days
