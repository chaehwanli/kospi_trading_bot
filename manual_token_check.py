import requests
import json
import os
from config import settings

MODE = "PROD" # Force PROD for check
BASE_URL = settings.URL_REAL
APP_KEY = settings.APP_KEY_REAL
APP_SECRET = settings.APP_SECRET_REAL

print(f"Mode: {MODE}")
print(f"Base URL: {BASE_URL}")
print(f"App Key: {APP_KEY[:5]}...")

# 1. Get Token
token_url = f"{BASE_URL}/oauth2/tokenP"
headers = {"content-type": "application/json"}
data = {
    "grant_type": "client_credentials",
    "appkey": APP_KEY,
    "secretkey": APP_SECRET
}

print(f"Requesting token from {token_url}...")
try:
    res = requests.post(token_url, headers=headers, data=json.dumps(data))
    print(f"Status: {res.status_code}")
    if res.status_code != 200:
        print(f"Error: {res.text}")
        exit(1)
        
    token_data = res.json()
    access_token = token_data.get('access_token')
    print(f"Token Received: {access_token[:10]}...")
    
    # 2. Test Data Fetch (OHLCV)
    # ka10080
    chart_url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"
    
    # Headers typically require:
    # Authorization: Bearer <token>
    # appkey: <appkey>
    # appsecret: <secret>
    # tr_id: FHKST01010100 (Real) or FHKST01010100 (Paper?? Check docs)
    # For Paper/Mock, tr_id might be different?
    # Usually: FHKST01010100 is for minute chart.
    
    # Let's verify tr_id mapping.
    # The library uses 'ka10080' which is the operation ID, but REST header needs tr_id.
    # From KIS docs: Minute Chart is FHKST01010100.
    
    headers_chart = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {access_token}",
        "appkey": APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id": "FHKST01010100", # Minute Chart
        "custtype": "P" # P for Person/Paper? Usually P.
    }
    
    params = {
        "fid_etc_cls_code": "",
        "fid_cond_mrkt_div_code": "J",
        "fid_input_iscd": "005930",
        "fid_input_hour_1": "60", # 60 minute
        "fid_pw_data_incu_yn": "N" 
    }
    
    print("Requesting OHLCV...")
    res_chart = requests.get(chart_url, headers=headers_chart, params=params)
    print(f"Chart Status: {res_chart.status_code}")
    print(f"Chart Body: {res_chart.text[:200]}")
    
except Exception as e:
    print(f"Exception: {e}")
