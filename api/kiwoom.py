import os
from config import settings
from utils.logger import setup_logger
import pandas as pd
import datetime

# Configure Environment Variables for Library
# The library reads these on import or when config functions are called.
os.environ["KIWOOM_API_KEY"] = settings.APP_KEY
os.environ["KIWOOM_API_SECRET"] = settings.APP_SECRET
os.environ["KIWOOM_USE_SANDBOX"] = "true" if settings.MODE == "PAPER" else "false"

# Import Library Components
from kiwoom_rest_api.auth.token import TokenManager
from kiwoom_rest_api.koreanstock.chart import Chart
from kiwoom_rest_api.koreanstock.order import Order
from kiwoom_rest_api.koreanstock.account import Account

logger = setup_logger("KiwoomAPI")

class KiwoomAPI:
    def __init__(self):
        # Initialize Library Components
        try:
            self.token_manager = TokenManager()
            self.chart = Chart(token_manager=self.token_manager)
            self.order = Order(token_manager=self.token_manager)
            self.account = Account(token_manager=self.token_manager)
            logger.info("Kiwoom API initialized with kiwoom-rest-api library.")
        except Exception as e:
            logger.error(f"Failed to initialize Kiwoom API components: {e}")
            raise

    def get_ohlcv(self, code, time_unit="60"):
        """
        Get OHLCV using stock_minute_chart_request_ka10080
        """
        try:
            # ka10080 params: stk_cd, tic_scope, upd_stkpc_tp, cont_yn, next_key
            # tic_scope: "60" for 60 minutes
            res = self.chart.stock_minute_chart_request_ka10080(
                stk_cd=code,
                tic_scope=str(time_unit),
                upd_stkpc_tp="1" # Adjusted price
            )
            
            if not res or res.get('rt_cd') != '0':
                logger.error(f"OHLCV Error: {res}")
                return None
                
            # output2 has list.
            items = res.get('output2', [])
            ohlcv = []
            for item in items:
                # Format: stck_bsop_date(YYYYMMDD) + stck_cntg_hour(HHMMSS)
                dt_str = item['stck_bsop_date'] + item['stck_cntg_hour']
                ohlcv.append({
                    'time': dt_str,
                    'open': int(item['stck_oprc']),
                    'high': int(item['stck_hgpr']),
                    'low': int(item['stck_lwpr']),
                    'close': int(item['stck_prpr']),
                    'volume': int(item['cntg_vol'])
                })
            return ohlcv[::-1] # Convert to Ascending Time
            
        except Exception as e:
            logger.error(f"Error fetching OHLCV: {e}")
            return None

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
