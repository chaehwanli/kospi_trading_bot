from config import settings
import kiwoom_rest_api.config
kiwoom_rest_api.config.API_KEY = settings.APP_KEY
kiwoom_rest_api.config.API_SECRET = settings.APP_SECRET
kiwoom_rest_api.config.USE_SANDBOX = True if settings.MODE == "PAPER" else False

from kiwoom_rest_api.auth.token import TokenManager
import os

tm = TokenManager()
print(f"Token Path (attr check): {getattr(tm, 'token_path', 'Not Found')}")
# Inspect obscure attributes
print(f"Dir: {dir(tm)}")

# Check if we can infer it
# Commonly it is 'kiwoom_token.dat' in cwd or tmp.
