import requests
import json
import time
import os
from datetime import datetime
from config import settings
from utils.logger import setup_logger

logger = setup_logger("KiwoomAPI")

class KiwoomAPI:
    def __init__(self):
        self.base_url = settings.BASE_URL
        self.app_key = settings.APP_KEY
        self.app_secret = settings.APP_SECRET
        self.account_no = settings.ACCOUNT_NO
        self.access_token = None
        self.token_expiry = 0
        
        self.token_file = "token.json"
        self._load_token()
        
    def _load_token(self):
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    data = json.load(f)
                    self.access_token = data.get('access_token')
                    self.token_expiry = data.get('token_expiry', 0)
            except Exception as e:
                logger.error(f"Failed to load token: {e}")

    def _save_token(self):
        with open(self.token_file, 'w') as f:
            json.dump({
                'access_token': self.access_token,
                'token_expiry': self.token_expiry
            }, f)

    def get_access_token(self):
        if self.access_token and time.time() < self.token_expiry:
            return self.access_token
            
        # URL for Token: Usually /oauth2/token
        url = f"{self.base_url}/oauth2/token"
        headers = {"content-type": "application/x-www-form-urlencoded"} # Standard OAuth2
        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        try:
            res = requests.post(url, headers=headers, data=body)
            res.raise_for_status()
            data = res.json()
            self.access_token = data['access_token']
            self.token_expiry = time.time() + int(data.get('expires_in', 86400)) - 60
            self._save_token()
            logger.info("Access token refreshed successfully")
            return self.access_token
        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            raise

    def get_headers(self, tr_id=None):
        token = self.get_access_token()
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "authorization": f"Bearer {token}",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
        }
        if tr_id:
            headers["tr_id"] = tr_id # Some APIs require TR ID in header
        return headers

    def call_tr(self, tr_id, payload):
        # Generic TR dispatch. Path structure assumption: /openapi/real/tr/dispatch or similar
        # NOTE: Exact path needs verification from official internal docs.
        # Assuming /tr/{tr_id} or /openapi/tr/{tr_id} based on REST trends.
        # Using a generic path placeholder.
        
        # Scenario A: Path is tr_id dependent
        # url = f"{self.base_url}/openapi/tr/{tr_id}"
        
        # Scenario B: Single Dispatch Endpoint
        url = f"{self.base_url}/openapi/tr/dispatch" 
        
        headers = self.get_headers(tr_id)
        try:
            res = requests.post(url, headers=headers, data=json.dumps(payload))
            res.raise_for_status()
            return res.json()
        except Exception as e:
            logger.error(f"TR {tr_id} Failed: {e}")
            return None

    def get_ohlcv(self, code, time_unit="60"):
        # TR Code for OHLCV: Unknown publically for REST. 
        # Using Placeholder 'OPT10081' (Daily) or equivalent REST ID.
        # TODO: User must verify this TR ID.
        tr_id = "ka10001" # Using Stock Info as placeholder for now, or finding generic candle TR.
        
        # Construct payload fitting Kiwoom REST spec
        payload = {
            "itm_no": code,
            "fid_cond_mrkt_div_code": "J",
            "fid_input_hour_1": time_unit
        }
        
        data = self.call_tr(tr_id, payload)
        if not data: return None
        
        # Parse logic would depend on response structure
        # ...
        return []

    def get_balance(self):
        # TR Code for Balance: kt00004 or similar
        tr_id = "kt00004"
        payload = {
            "acnt_no": self.account_no,
        }
        data = self.call_tr(tr_id, payload)
        if not data: return None
        # Parse return...
        return 1000000 # Mock return until parser implemented

    def place_order(self, code, qty, order_type="BUY", price=0):
        # TR for Order: kt10000 (Buy), kt10001 (Sell)
        tr_id = "kt10000" if order_type == "BUY" else "kt10001"
        payload = {
            "ord_qty": str(qty),
            "ord_prc": str(price),
            "itm_no": code,
            "acnt_no": self.account_no
        }
        return self.call_tr(tr_id, payload)
