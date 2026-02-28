# gigachat_provider.py
# SECURE GIGACHAT PROVIDER (PRODUCTION SAFE)

import os
import time
import httpx
import base64
import uuid
from dotenv import load_dotenv


# ==========================================
# LOAD ENV
# ==========================================

load_dotenv()

CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")

if not CLIENT_ID or not CLIENT_SECRET:
    raise RuntimeError("GigaChat environment variables not set")


TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"


class GigaChatProvider:

    def __init__(self):
        self.token = None
        self.expire = 0


    # ==========================================
    # GET TOKEN (CACHED)
    # ==========================================

    async def get_token(self):

        if self.token and time.time() < self.expire:
            return self.token

        basic_auth = f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
        basic_auth_b64 = base64.b64encode(basic_auth).decode()

        headers = {
            "Authorization": f"Basic {basic_auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4())
        }

        data = {
            "scope": "GIGACHAT_API_PERS"
        }

        async with httpx.AsyncClient(
                timeout=30
        ) as client:

            response = await client.post(
                TOKEN_URL,
                headers=headers,
                data=data
            )

        if response.status_code != 200:
            raise Exception(f"OAuth error: {response.status_code}")

        token_json = response.json()
        self.token = token_json["access_token"]
        self.expire = time.time() + 1700

        return self.token


    # ==========================================
    # GENERATE RESPONSE
    # ==========================================

    async def generate(self, messages: list):

        token = await self.get_token()

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "GigaChat",
            "messages": messages,
            "temperature": 0.7,
            "stream": False
        }

        async with httpx.AsyncClient(
                timeout=60
        ) as client:

            response = await client.post(
                CHAT_URL,
                headers=headers,
                json=payload
            )

        if response.status_code != 200:
            raise Exception(f"GigaChat error: {response.status_code}")

        result = response.json()

        try:
            content = result["choices"][0]["message"]["content"]
        except Exception:
            content = "Ошибка получения ответа"

        return content