from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict
import os
import traceback

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

from chat_memory import save_message, load_history
from providers.gigachat_provider import GigaChatProvider
from prompt.emotional_state import EmotionalState
from prompt.sacred_personality import SacredPersonality
from prompt.dialogue_governor import DialogueGovernor


limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="AI Server", version="17.0-governor-integrated")

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

FRONTEND_URL = os.getenv("FRONTEND_URL", "*")
SERVER_API_KEY = os.getenv("SERVER_API_KEY")

if not SERVER_API_KEY:
    raise RuntimeError("SERVER_API_KEY not set in environment")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL] if FRONTEND_URL != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("=== AI SERVER STARTED (GOVERNOR MODE) ===")

ai_provider = GigaChatProvider()
sacred_personality = SacredPersonality()
dialogue_governor = DialogueGovernor()


def verify_api_key(x_api_key: str):
    if x_api_key != SERVER_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")


@app.post("/chat")
@limiter.limit("20/minute")
async def chat(request: Request, x_api_key: str = Header(...)):

    try:
        verify_api_key(x_api_key)

        body = await request.json()
        message = body.get("message")

        if not message:
            return JSONResponse(
                status_code=400,
                content={"error": "Message field required"}
            )

        chat_id = "default_user"
        history = load_history(chat_id)

        messages: List[Dict[str, str]] = []

        # ==============================
        # SYSTEM MESSAGE (ONLY ONE!)
        # ==============================

        system_message = sacred_personality.build_system_message()

        emotional_state = EmotionalState()
        emotional_state.update_from_text(message)

        # Добавляем эмоциональный контекст
        system_message["content"] += "\n\n" + emotional_state.build_context()["content"]

        # ==============================
        # GOVERNOR (SOFT INTEGRATION)
        # ==============================

        governor_message = dialogue_governor.build_governor_message(history + [{"role": "user", "content": message}])

        # ВАЖНО: не создаём второй system.
        # Добавляем инструкции внутрь основного system.
        system_message["content"] += "\n\n" + governor_message["content"]

        messages.append(system_message)

        # ==============================
        # HISTORY
        # ==============================

        for msg in history:
            if msg["role"] != "system":
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        # ==============================
        # USER MESSAGE
        # ==============================

        messages.append({
            "role": "user",
            "content": message
        })

        content = await ai_provider.generate(messages)

        save_message(chat_id, "user", message)
        save_message(chat_id, "assistant", content)

        return JSONResponse({"response": content})

    except Exception as e:
        print("🔥 CHAT CRASH:")
        traceback.print_exc()
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/")
async def root():
    return {
        "status": "ok",
        "provider": "gigachat",
        "mode": "governor-integrated"
    }