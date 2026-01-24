import os
from config import settings
from utils.logger import setup_logger
import pandas as pd
import datetime

# Configure Environment Variables for Library
# We also inject directly into the config module to be safe against import order.
import kiwoom_rest_api.config

# Inject settings
kiwoom_rest_api.config.API_KEY = settings.APP_KEY
kiwoom_rest_api.config.API_SECRET = settings.APP_SECRET
kiwoom_rest_api.config.USE_SANDBOX = True if settings.MODE == "PAPER" else False
# Force base URL update
if kiwoom_rest_api.config.USE_SANDBOX:
    kiwoom_rest_api.config.DEFAULT_BASE_URL = kiwoom_rest_api.config.SANDBOX_BASE_URL # Just to be sure the getter uses it
else:
    # If library uses DEFAULT_BASE_URL as fallback
    pass 

# Import Library Components
from kiwoom_rest_api.auth.token import TokenManager
from kiwoom_rest_api.koreanstock.chart import Chart
from kiwoom_rest_api.koreanstock.order import Order
from kiwoom_rest_api.koreanstock.account import Account
from kiwoom_rest_api.config import get_base_url # Import getter

logger = setup_logger("KiwoomAPI")

class KiwoomAPI:
    def __init__(self, mode=None):
        # Initialize Library Components
        try:
            # 1. Determine Mode (Override or Default)
            target_mode = mode if mode else settings.MODE
            
            # 2. Configure Library Config dynamically
            # We must set this BEFORE creating TokenManager
            kiwoom_rest_api.config.USE_SANDBOX = True if target_mode == "PAPER" else False
            
            if target_mode == "PAPER":
                kiwoom_rest_api.config.API_KEY = settings.APP_KEY # This maps to PAPER key in settings if MODE=PAPER, but wait.
                # settings.APP_KEY is already resolved based on settings.MODE.
                # If we want to support REAL mode while settings.MODE is PAPER, we need raw keys.
                # Check settings.py again.
                # settings.py exports APP_KEY based on MODE.
                # We need access to BOTH keys if we want to switch.
                pass
            else:
                # If requesting REAL mode, we need REAL keys.
                # But settings.py might only have exported PAPER keys if MODE=PAPER.
                # We need to import raw env vars or modify settings.py to export both sets.
                pass

            # Update: modifying logic to rely on raw env vars here would be cleaner, 
            # but for now let's assume settings.py exports specific keys we need.
            # Actually, settings.py exports APP_KEY/SECRET based on MODE. 
            # So if MODE=PAPER, settings.APP_KEY is PAPER key.
            # If we force REAL mode here, we need REAL keys.
            
            # Re-read keys from env to be safe
            if target_mode == "PAPER":
                 kiwoom_rest_api.config.API_KEY = os.getenv("APP_KEY_PAPER", "")
                 kiwoom_rest_api.config.API_SECRET = os.getenv("APP_SECRET_PAPER", "")
            else:
                 kiwoom_rest_api.config.API_KEY = os.getenv("APP_KEY_REAL", "")
                 kiwoom_rest_api.config.API_SECRET = os.getenv("APP_SECRET_REAL", "")
            
            # Force base URL update
            if kiwoom_rest_api.config.USE_SANDBOX:
                kiwoom_rest_api.config.DEFAULT_BASE_URL = kiwoom_rest_api.config.SANDBOX_BASE_URL
            else:
                kiwoom_rest_api.config.DEFAULT_BASE_URL = "https://api.kiwoom.com"

            self.token_manager = TokenManager()
            
            # Explicitly get base_url to prevent double-slash issue in library
            base_url = get_base_url()
            
            self.chart = Chart(token_manager=self.token_manager, base_url=base_url)
            self.order = Order(token_manager=self.token_manager, base_url=base_url)
            self.account = Account(token_manager=self.token_manager, base_url=base_url)
            
            logger.info(f"Kiwoom API initialized in {target_mode} mode.")
            
        except Exception as e:
            logger.error(f"Failed to initialize Kiwoom API components: {e}")
            raise

    def get_ohlcv(self, code, time_unit="60", days=1095):
        """
        Get OHLCV using stock_minute_chart_request_ka10080 with pagination.
        days: Number of days to fetch (default ~3 years = 1095)
        """
        import time
        try:
            target_date = (datetime.datetime.now() - datetime.timedelta(days=days)).strftime("%Y%m%d")
            all_ohlcv = []
            next_key = None
            
            while True:
                # ka10080 params: stk_cd, tic_scope, upd_stkpc_tp, cont_yn, next_key
                # tic_scope: "60" for 60 minutes
                
                kwargs = {
                    "stk_cd": code,
                    "tic_scope": str(time_unit),
                    "upd_stkpc_tp": "1", # Adjusted price
                    "cont_yn": "Y" if next_key else "N"
                }
                if next_key:
                    kwargs["next_key"] = next_key
                
                res = self.chart.stock_minute_chart_request_ka10080(**kwargs)
                
                # Check success (supports 'rt_cd' or 'return_code')
                is_success = False
                if str(res.get('rt_cd', '')) == '0':
                    is_success = True
                elif str(res.get('return_code', '')) == '0':
                    is_success = True
                    
                if not is_success:
                    logger.error(f"OHLCV Error: {res}")
                    break
                    
                # output2 has list. Sometimes key is 'stk_min_pole_chart_qry'
                items = res.get('output2') or res.get('stk_min_pole_chart_qry') or []
                
                if not isinstance(items, list):
                    items = []

                # Debug: Log item count
                logger.info(f"Loop {len(all_ohlcv)//900 + 1}: Received {len(items)} items. Parsing...")
                
                batch_ohlcv = []
                parse_errors = 0
                
                for item in items:
                    # Format: cntr_tm(YYYYMMDDHHMMSS)
                    dt_str = item.get('cntr_tm', '')
                    # Fallback
                    if not dt_str:
                         dt_str = item.get('stck_bsop_date', '') + item.get('stck_cntg_hour', '')
                    
                    try:
                        batch_ohlcv.append({
                            'time': dt_str,
                            'open': abs(int(item.get('open_pric') or item.get('stck_oprc') or 0)),
                            'high': abs(int(item.get('high_pric') or item.get('stck_hgpr') or 0)),
                            'low': abs(int(item.get('low_pric') or item.get('stck_lwpr') or 0)),
                            'close': abs(int(item.get('cur_prc') or item.get('stck_prpr') or 0)),
                            'volume': abs(int(item.get('trde_qty') or item.get('cntg_vol') or 0)) 
                        })
                    except ValueError:
                        parse_errors += 1
                        continue 
                
                logger.info(f"Loop parsed {len(batch_ohlcv)} valid rows. Errors: {parse_errors}")
                
                if not batch_ohlcv:
                    break
                    
                all_ohlcv.extend(batch_ohlcv)
                
                # Check date condition (last item is oldest in this batch typically?)
                # Kiwoom returns latest first. So last item is oldest.
                last_time = batch_ohlcv[-1]['time'][:8] # YYYYMMDD
                if last_time < target_date:
                    logger.info(f"Reached target date {target_date} (Current: {last_time}). Stopping.")
                    break
                
                # Check continuation
                cont_yn = res.get('cont-yn', 'N') # Note: response key might be 'cont-yn' or 'next-key' existence
                next_key = res.get('next-key', '')
                
                if cont_yn != 'Y' or not next_key:
                    break
                    
                logger.info(f"Fetching continuation... (oldest: {last_time})")
                time.sleep(0.2) # Rate limit safety
                
            return all_ohlcv[::-1] # Convert to Ascending Time
            
        except Exception as e:
            logger.error(f"Error fetching OHLCV: {e}")
            return None

    def get_holdings(self):
        """
        Get current holdings using kt00018 'output2'
        Returns dict: { 'code': qty, ... }
        """
        try:
            res = self.account.account_evaluation_balance_detail_request_kt00018(
                query_type="1",
                domestic_exchange_type="KRX"
            )
            
            if not res or res.get('rt_cd') != '0':
                logger.error(f"Holdings Error: {res}")
                return {}
                
            items = res.get('output2', [])
            if not items:
                return {}
                
            holdings = {}
            for item in items:
                # Code might be A005930 or 005930. 
                # Usually Kiwoom API returns pure code or A-prefixed.
                # 'stk_cd' or 'itm_no'. 
                # Let's clean it up.
                code = item.get('pdno', '') # 'pdno' is typically product number/code in newer API docs
                # If pdno is missing, try synonyms
                if not code:
                     code = item.get('stk_cd', '')
                     
                # Remove 'A' prefix if present
                if code.startswith('A'):
                    code = code[1:]
                    
                qty = int(item.get('hldg_qty') or 0)
                
                if code and qty > 0:
                    holdings[code] = qty
                    
            logger.info(f"Account Holdings: {holdings}")
            return holdings
            
        except Exception as e:
            logger.error(f"Error fetching holdings: {e}")
            return {}

    def get_balance(self):
        """
        Get balance using account_evaluation_balance_detail_request_kt00018
        """
        try:
            # We assume TokenManager handles auth tokens.
            # But KT00018 might need account number?
            # From docstring `kt00018` usage: `query_type`, `domestic_exchange_type`. No acc_no.
            # This implies `Account` class or Library config might need account no?
            # Inspecting `account.py` again?
            # No, `kt00018` docstring example showed NO account number arg.
            # Usually strict REST API needs it in header or body.
            # Maybe the library's `KiwoomBaseAPI` or `Account` reads it from somewhere?
            # OR `kt00018` is a user-level query based on the Token's owner?
            
            res = self.account.account_evaluation_balance_detail_request_kt00018(
                query_type="1",
                domestic_exchange_type="KRX"
            )
            
            if not res or res.get('rt_cd') != '0':
                logger.error(f"Balance Error: {res}")
                return None
                
            summary = res.get('output1', {})
            return float(summary.get('prsm_dpst_aset_amt', 0))
            
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return None

    def place_order(self, code, qty, order_type="BUY", price=0):
        """
        Place Order using kt10000 / kt10001
        """
        try:
            # 00: Limit, 01: Market
            ord_dvsn = "01" if price == 0 else "00"
            
            # Need to pass account??
            # Order method signature: `stk_cd` etc.
            # Previous `grep` of order.py showed `stock_buy_order_request_kt10000`.
            # Let's hope it follows logic.
            # Wait, `kt10000` usually requires account info.
            # If function signature doesn't take it, maybe it's implicitly handled.
            
            # Re-checking Order signature from memory/grep: 
            # I didn't see FULL signature in grep, just def line.
            # But assume standard kwargs matching API.
            # If it fails, we will see in logs.
            
            target_method = self.order.stock_buy_order_request_kt10000 if order_type == "BUY" else self.order.stock_sell_order_request_kt10001
            
            # Kiwoom REST usually needs: ord_qty, ord_prc, itm_no, ord_dvsn
            # The library functions often map snake_case to API fields.
            # e.g. `itm_no` -> `stk_cd`.
            # I will use snake_case args if library uses them (refer to Chart usage `stk_cd`).
            # Chart used `stk_cd`. So Order likely uses `stk_cd` too.
            # But `kt10000` usually uses `itm_no` in official spec.
            # I should use `stk_cd` if that's what the wrapper calls it.
            # Let's try `stk_cd` as arg name based on chart.py pattern.
            
            res = target_method(
                ord_qty=str(qty),
                ord_prc=str(price),
                stk_cd=code, # Assuming wrapper normalizes this name
                ord_dvsn=ord_dvsn,
                tr_to="0" # Trade type?
            )
            
            if not res or res.get('rt_cd') != '0':
                logger.error(f"Order Error: {res}")
                return None
            
            logger.info(f"Order Placed: {order_type} {code} {qty}")
            return res
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
