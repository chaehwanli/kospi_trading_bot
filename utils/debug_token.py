import requests
import os
import sys
# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings

def test_token():
    print(f"--- Debugging Token (MODE: {settings.MODE}) ---")
    print(f"APP_KEY: {settings.APP_KEY[:5]}***")
    print(f"APP_SECRET: {settings.APP_SECRET[:5]}***")
    
    base_url = settings.URL_PAPER if settings.MODE == "PAPER" else settings.URL_REAL
    token_url = f"{base_url}/oauth2/token"
    
    print(f"Requesting Token from: {token_url}")
    
    headers = {
        "content-type": "application/x-www-form-urlencoded"
    }
    body = {
        "grant_type": "client_credentials",
        "appkey": settings.APP_KEY,
        "secretkey": settings.APP_SECRET 
    }
    
    # Note: The library might use 'secretkey' or 'appsecret'. 
    # Official docs usually say 'appsecret'. 
    # Let's try 'appsecret' first. 
    
    # Attempt 1: Form URL Encoded
    print("\n[Attempt 1] Form URL Encoded")
    try:
        res = requests.post(token_url, headers=headers, data=body)
        print(f"Status Code: {res.status_code}")
        if res.status_code == 200:
             print("SUCCESS (Form)!")
             print(res.json())
             return
        else:
             print(f"Failed: {res.text}")
    except Exception as e:
        print(f"Error: {e}")

    # Attempt 2: JSON
    print("\n[Attempt 2] JSON Body")
    headers['content-type'] = 'application/json'
    try:
        res = requests.post(token_url, headers=headers, json=body)
        print(f"Status Code: {res.status_code}")
        if res.status_code == 200:
            print("SUCCESS (JSON)!")
            print(res.json())
        else:
            print(f"Failed: {res.text}")
            try:
                err = res.json()
                if err.get('error') == 'invalid_client':
                    print("\n[Hint] invalid_client: Check Key/Secret or Mode (Paper vs Real).")
            except: pass
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_token()
