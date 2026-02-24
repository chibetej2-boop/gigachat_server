# token_manager.py
# PRODUCTION OAuth MANAGER FOR GIGACHAT

import time
import uuid
import base64
import requests

print("=== TOKEN MANAGER INITIALIZED ===")

# ВСТАВЬ СВОИ КЛЮЧИ
CLIENT_ID = "019ba702-cdba-7ffd-8f47-ef2d7a450f56"
CLIENT_SECRET = "80c73cdb-508b-480e-9ac4-9642c254707a"

OAUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"

_access_token = None
_expire_time = 0


def _fetch_token():
    global _access_token
    global _expire_time

    print("\n=== FETCHING NEW GIGACHAT TOKEN ===")

    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
    credentials_base64 = base64.b64encode(credentials.encode()).decode()

    headers = {
        "Authorization": f"Basic {credentials_base64}",
        "RqUID": str(uuid.uuid4()),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    data = {
        "grant_type": "client_credentials",
        "scope": "GIGACHAT_API_PERS"
    }

    response = requests.post(
        OAUTH_URL,
        headers=headers,
        data=data,
        verify=False,
        timeout=30,
    )

    print("STATUS:", response.status_code)
    print("BODY:", response.text)

    if response.status_code != 200:
        raise RuntimeError(
            f"OAuth error: {response.status_code} | {response.text}"
        )

    token_data = response.json()

    _access_token = token_data["access_token"]
    _expire_time = token_data["expires_at"] / 1000

    print("TOKEN RECEIVED")


def get_valid_token():
    global _access_token
    global _expire_time

    now = time.time()

    if not _access_token or now >= _expire_time - 60:
        _fetch_token()

    return _access_token