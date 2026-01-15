def get_tick_size(price):
    """
    Calculate the KOSPI tick size (minimum price fluctuation) based on the price range.
    
    Ranges (as of 2025/2026 anticipated):
    - < 1,000: 1
    - 1,000 <= price < 5,000: 5
    - 5,000 <= price < 10,000: 10
    - 10,000 <= price < 50,000: 50
    - 50,000 <= price < 100,000: 100
    - 100,000 <= price < 500,000: 500
    - >= 500,000: 1,000
    """
    if price < 1000:
        return 1
    elif price < 5000:
        return 5
    elif price < 10000:
        return 10
    elif price < 50000:
        return 50
    elif price < 100000:
        return 100
    elif price < 500000:
        return 500
    else:
        return 1000
