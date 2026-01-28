def get_tick_size(price, market_type="KOSPI"):
    """
    Calculate the Tick Size (minimum price fluctuation) based on price range and market type.
    
    KOSPI:
    - < 1,000: 1
    - 1,000 ~ 5,000: 5
    - 5,000 ~ 10,000: 10
    - 10,000 ~ 50,000: 50
    - 50,000 ~ 100,000: 100
    - 100,000 ~ 500,000: 500
    - >= 500,000: 1,000
    
    KOSDAQ:
    - < 1,000: 1
    - 1,000 ~ 5,000: 5
    - 5,000 ~ 10,000: 10
    - 10,000 ~ 50,000: 50
    - >= 50,000: 100 (Differs from KOSPI)
    """
    if price < 1000:
        return 1
    elif price < 5000:
        return 5
    elif price < 10000:
        return 10
    elif price < 50000:
        return 50
    else:
        # Above 50,000
        if market_type == "KOSDAQ":
            return 100
        else:
            # KOSPI Logic
            if price < 100000:
                return 100
            elif price < 500000:
                return 500
            else:
                return 1000
