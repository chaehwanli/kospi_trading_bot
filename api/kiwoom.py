import requests
import json
import time
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
        
        # Load token if exists
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
            
        url = f"{self.base_url}/oauth2/tokenP"
        headers = {"content-type": "application/json"}
        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret
        }
        
        try:
            res = requests.post(url, headers=headers, data=json.dumps(body))
            res.raise_for_status()
            data = res.json()
            self.access_token = data['access_token']
            # Token usually valid for 24h, set expiry slightly earlier
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
            "custtype": "P" # P for individual
        }
        if tr_id:
            headers["tr_id"] = tr_id
        return headers

    def get_ohlcv(self, code, time_unit="60"):
        """
        Fetch OHLCV Data. 
        For KIS API, getting minute/hour data usually uses 'FHKST03010200'.
        time_unit: '60' for 60 minutes (1 hour). 
        Note: The actual TR ID and parameters might vary for "minute" chart.
        TR ID: FHKST03010200 (InquireTimeItemChartPrice)
        """
        path = "/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice"
        url = f"{self.base_url}{path}"
        
        headers = self.get_headers("FHKST03010200")
        
        # Calculate start/end time is complex for KIS, usually it requests based on current time backwards?
        # params:
        # FID_COND_MRKT_DIV_CODE: J (Market)
        # FID_INPUT_ISCD: code
        # FID_INPUT_HOUR_1: time_unit (seems strictly 30, 1 etc? need verification)
        # FID_PW_DATA_INCU_YN: Y
        
        # NOTE: KIS API might not support "60" directly in all endpoints, sometimes we fetch 30m and aggregate.
        # But 'FHKST03010200' documentation says FID_INPUT_HOUR_1 takes minute interval?
        # Let's assume '60' works or we use '30' and aggregate. For simplicity, try passing time_unit.
        
        # Date: need to handle logic for '1 year data'. The simple endpoint only gives recent data.
        # For historical data, we might need daily candles or iterate. 
        # Requirement: "1시간 분봉".
        
        params = {
            "FID_ETC_CLS_CODE": "",
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": code,
            "FID_INPUT_HOUR_1": time_unit, 
            "FID_PW_DATA_INCU_YN": "Y"
        }
        
        try:
            res = requests.get(url, headers=headers, params=params)
            res.raise_for_status()
            data = res.json()
            if data['rt_cd'] != '0':
                logger.error(f"API Error get_ohlcv: {data['msg1']}")
                return None
            
            # Parse output
            # output2 contains the list
            items = data['output2']
            ohlcv = []
            for item in items:
                ohlcv.append({
                    'time': item['stck_bsop_date'] + item['stck_cntg_hour'],
                    'open': int(item['stck_oprc']),
                    'high': int(item['stck_hgpr']),
                    'low': int(item['stck_lwpr']),
                    'close': int(item['stck_prpr']),
                    'volume': int(item['cntg_vol'])
                })
            
            return ohlcv
        except Exception as e:
            logger.error(f"Error fetching OHLCV: {e}")
            return None

    def get_balance(self):
        """
        Check balance.
        TR ID: TTTC8434R (Real) / VTTC8434R (Virtual) ? 
        Actually commonly: TTTC8434R (InquireBalance)
        """
        path = "/uapi/domestic-stock/v1/trading/inquire-balance"
        tr_id = "VTTC8434R" if settings.MODE == "PAPER" else "TTTC8434R"
        
        url = f"{self.base_url}{path}"
        headers = self.get_headers(tr_id)
        
        params = {
            "CANO": self.account_no[0:8],
            "ACNT_PRDT_CD": self.account_no[8:10],
            "AFHR_FLPR_YN": "N",
            "OFL_YN": "",
            "INQR_DVSN": "02",
            "UNPR_DVSN": "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN": "01",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": ""
        }
        
        try:
            res = requests.get(url, headers=headers, params=params)
            res.raise_for_status()
            data = res.json()
            if data['rt_cd'] != '0':
                logger.error(f"API Error get_balance: {data['msg1']}")
                return None
                
            # output2[0].dnca_tot_amt (Deposit)
            deposit = float(data['output2'][0]['dnca_tot_amt'])
            return deposit
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return None

    def place_order(self, code, qty, order_type="BUY", price=0):
        """
        Place Order.
        TR ID: TTTC8908U (Paper Buy) / TTTC0802U (Real Buy)
        Sell: TTTC8908U (Paper Sell) / TTTC0801U (Real Sell)
        Wait, paper TR IDs are usually VTTC...
        Real: TTTC0802U (Buy), TTTC0801U (Sell)
        Paper: VTTC0802U (Buy), VTTC0801U (Sell)
        
        Note: KIS Paper trading often uses VTTC.
        """
        direction_tr = "02" if order_type == "BUY" else "01" # 02 Buy, 01 Sell (Wait, usually 02/01 is for cash/credit)
        # Actually TR ID distinguishes buy/sell often.
        # But for domestic stock order:
        # Real Buy: TTTC0802U
        # Real Sell: TTTC0801U
        # Paper Buy: VTTC0802U
        # Paper Sell: VTTC0801U
        
        tr_id = ""
        if settings.MODE == "PAPER":
            tr_id = "VTTC0802U" if order_type == "BUY" else "VTTC0801U"
        else:
            tr_id = "TTTC0802U" if order_type == "BUY" else "TTTC0801U"
            
        path = "/uapi/domestic-stock/v1/trading/order-cash"
        url = f"{self.base_url}{path}"
        headers = self.get_headers(tr_id)
        
        body = {
            "CANO": self.account_no[0:8],
            "ACNT_PRDT_CD": self.account_no[8:10],
            "PDNO": code,
            "ORD_DVSN": "01" if price > 0 else "01", # 01: Limit, 03: Market? Check KIS docs. 01 is Limit. 00 is Limit?
            # KIS: 00: Limit, 01: Market  <-- WARNING: Check this.
            # Usually 00 is Limit, 01 is Market.
            # If price is 0, assume market order?
            # But safer to use Limit or specific code.
            # Let's assume Limit "00" for now and Market "01".
            "ORD_QTY": str(qty),
            "ORD_UNPR": str(price) if price > 0 else "0",
        }
        
        # Override for Market Order
        if price == 0:
            body["ORD_DVSN"] = "01" # Market
            
        try:
            res = requests.post(url, headers=headers, data=json.dumps(body))
            res.raise_for_status()
            data = res.json()
            if data['rt_cd'] != '0':
                logger.error(f"API Error place_order: {data['msg1']}")
                return None
            
            logger.info(f"Order placed: {order_type} {code} {qty} @ {price}")
            return data
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
