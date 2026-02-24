import time
import httpx
import base64
import uuid

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel


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


# =====================================
# APP INIT
# =====================================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("=== GIGACHAT SERVER STARTED ===")


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

        print("\n=== FETCHING NEW TOKEN ===")

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

        async with httpx.AsyncClient(verify=False, timeout=30) as client:

            response = await client.post(
                TOKEN_URL,
                headers=headers,
                data=data,
            )

        print("TOKEN STATUS:", response.status_code)
        print("TOKEN BODY:", response.text)

        if response.status_code != 200:
            raise Exception("OAuth error")

        token_json = response.json()

        self.token = token_json["access_token"]

        self.expire = time.time() + 1800

        print("✅ TOKEN RECEIVED")

        return self.token


token_manager = TokenManager()


# =====================================
# CHAT STREAM
# =====================================

@app.post("/chat_stream")
async def chat_stream(request: ChatRequest):

    user_message = request.message

    print("\n=== CHAT REQUEST ===")
    print("USER:", user_message)

    token = await token_manager.get_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "GigaChat",
        "messages": [
            {
                "role": "user",
                "content": user_message
            }
        ],
        "temperature": 0.7,
        "stream": True
    }


    async def generate():

        async with httpx.AsyncClient(
            verify=False,
            timeout=None
        ) as client:

            async with client.stream(
                "POST",
                CHAT_URL,
                headers=headers,
                json=payload
            ) as response:

                print("GIGACHAT STATUS:", response.status_code)

                if response.status_code != 200:

                    error_text = await response.aread()

                    print("❌ GIGACHAT ERROR:", error_text)

                    yield "ERROR"

                    return


                async for chunk in response.aiter_text():

                    if not chunk.strip():
                        continue

                    yield chunk


    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


# =====================================
# CHAT HISTORY
# =====================================

@app.post("/chat_history")
async def chat_history():

    return JSONResponse({
        "messages": []
    })


# =====================================
# ROOT
# =====================================

@app.get("/")
async def root():

    return {
        "status": "ok",
        "server": "gigachat"
    } 