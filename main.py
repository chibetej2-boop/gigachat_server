from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict
import os

from chat_memory import save_message, load_history
from providers.gigachat_provider import GigaChatProvider
from prompt.emotional_state import EmotionalState


# =====================================
# REQUEST MODEL
# =====================================

class ChatRequest(BaseModel):
    message: str
    chat_id: str


# =====================================
# APP INIT
# =====================================

app = FastAPI(
    title="AI Server",
    version="8.0"
)

# =====================================
# SECURE CORS CONFIG
# =====================================

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  # Разрешён только конкретный фронтенд
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["Content-Type", "Authorization"],
)

print("=== AI SERVER STARTED (SECURE MODE ACTIVE) ===")


# =====================================
# PROVIDER INIT
# =====================================

ai_provider = GigaChatProvider()


# =====================================
# CHAT
# =====================================

@app.post("/chat")
async def chat(request: ChatRequest):

    history = load_history(request.chat_id)

    messages: List[Dict[str, str]] = []

    # ===== LOAD HISTORY =====
    for msg in history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    # ===== EMOTIONAL LAYER =====
    emotional_state = EmotionalState()
    emotional_state.update_from_text(request.message)

    messages.append(emotional_state.build_context())

    # ===== USER MESSAGE =====
    messages.append({
        "role": "user",
        "content": request.message
    })

    try:
        content = await ai_provider.generate(messages)

    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "AI provider error"}
        )

    save_message(request.chat_id, "user", request.message)
    save_message(request.chat_id, "assistant", content)

    return JSONResponse({
        "response": content
    })


# =====================================
# CHAT HISTORY
# =====================================

@app.post("/chat_history")
async def chat_history(request: ChatRequest):

    history = load_history(request.chat_id)

    return JSONResponse({
        "messages": history
    })


# =====================================
# ROOT
# =====================================

@app.get("/")
async def root():
    return {
        "status": "ok",
        "provider": "gigachat",
        "memory": "supabase",
        "emotional_layer": "active",
        "security": "cors-restricted"
    }