import time
import httpx
import base64
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional


# =====================================
# CONFIG
# =====================================

CLIENT_ID = "019ba702-cdba-7ffd-8f47-ef2d7a450f56"
CLIENT_SECRET = "80c73cdb-508b-480e-9ac4-9642c254707a"

TOKEN_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"


# =====================================
# REQUEST MODEL
# =====================================

class ChatRequest(BaseModel):
    message: str
    chat_id: Optional[str] = None


# =====================================
# APP INIT
# =====================================

app = FastAPI(title="GigaChat Server", version="4.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("=== GIGACHAT SERVER STARTED (NO STREAM) ===")


# =====================================
# TOKEN MANAGER
# =====================================

class TokenManager:
    def __init__(self):
        self.token = None
        self.expire = 0

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

        data = {"scope": "GIGACHAT_API_PERS"}

        async with httpx.AsyncClient(verify=False, timeout=30) as client:
            response = await client.post(
                TOKEN_URL,
                headers=headers,
                data=data
            )

        if response.status_code != 200:
            raise Exception("OAuth error")

        token_json = response.json()
        self.token = token_json["access_token"]
        self.expire = time.time() + 1700

        return self.token


token_manager = TokenManager()


# =====================================
# CHAT (NO STREAM)
# =====================================

@app.post("/chat")
async def chat(request: ChatRequest):

    token = await token_manager.get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "GigaChat",
        "messages": [
            {"role": "user", "content": request.message}
        ],
        "temperature": 0.7,
        "stream": False
    }

    async with httpx.AsyncClient(verify=False, timeout=60) as client:
        response = await client.post(
            CHAT_URL,
            headers=headers,
            json=payload
        )

    if response.status_code != 200:
        return JSONResponse(
            status_code=500,
            content={"error": "GigaChat error"}
        )

    result = response.json()

    try:
        content = result["choices"][0]["message"]["content"]
    except:
        content = "Ошибка получения ответа"

    return JSONResponse({"response": content})


# =====================================
# ROOT
# =====================================

@app.get("/")
async def root():
    return {"status": "ok", "server": "gigachat"}
