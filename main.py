from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict

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
    version="7.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # позже заменим на фронт
    allow_credentials=True,
    allow_methods=["POST"],
    allow_headers=["*"],
)

print("=== AI SERVER STARTED (EMOTIONAL LAYER ACTIVE) ===")


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

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
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
        "emotional_layer": "active"
    }