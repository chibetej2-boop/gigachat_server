from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict
import os

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

from chat_memory import save_message, load_history
from providers.gigachat_provider import GigaChatProvider
from prompt.emotional_state import EmotionalState


# =====================================
# RATE LIMITER
# =====================================

limiter = Limiter(key_func=get_remote_address)


# =====================================
# APP INIT
# =====================================

app = FastAPI(
    title="AI Server",
    version="13.0"
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


# =====================================
# ENV SECURITY
# =====================================

FRONTEND_URL = os.getenv("FRONTEND_URL", "*")
SERVER_API_KEY = os.getenv("SERVER_API_KEY")

if not SERVER_API_KEY:
    raise RuntimeError("SERVER_API_KEY not set in environment")


# =====================================
# CORS
# =====================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL] if FRONTEND_URL != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("=== AI SERVER STARTED (SAFE MODE) ===")


# =====================================
# PROVIDER INIT
# =====================================

ai_provider = GigaChatProvider()


# =====================================
# SECURITY CHECK
# =====================================

def verify_api_key(x_api_key: str):
    if x_api_key != SERVER_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")


# =====================================
# CHAT
# =====================================

@app.post("/chat")
@limiter.limit("20/minute")
async def chat(request: Request, x_api_key: str = Header(...)):

    verify_api_key(x_api_key)

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid JSON"}
        )

    message = body.get("message")

    if not message:
        return JSONResponse(
            status_code=400,
            content={"error": "Message field required"}
        )

    chat_id = "default_user"

    history = load_history(chat_id)

    messages: List[Dict[str, str]] = []

    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    emotional_state = EmotionalState()
    emotional_state.update_from_text(message)

    messages.append(emotional_state.build_context())

    messages.append({
        "role": "user",
        "content": message
    })

    try:
        content = await ai_provider.generate(messages)

    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "AI provider error"}
        )

    save_message(chat_id, "user", message)
    save_message(chat_id, "assistant", content)

    return JSONResponse({
        "response": content
    })


# =====================================
# ROOT
# =====================================

@app.get("/")
async def root():
    return {
        "status": "ok",
        "provider": "gigachat",
        "mode": "flutter-safe"
    }