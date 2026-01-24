from config import settings
import kiwoom_rest_api.config
import os

# Inject settings
kiwoom_rest_api.config.API_KEY = settings.APP_KEY
kiwoom_rest_api.config.API_SECRET = settings.APP_SECRET
kiwoom_rest_api.config.USE_SANDBOX = True if settings.MODE == "PAPER" else False

from kiwoom_rest_api.auth.token import TokenManager

print("Initializing TokenManager...")
tm = TokenManager()
if tm.access_token:
    print(f"Current Token (Masked): {tm.access_token[:10]}...")
else:
    print("Current Token: None")

print("Forcing New Token Request...")
tm._request_new_token()
print(f"New Token (Masked): {tm.access_token[:10]}...")
print("Done.")
