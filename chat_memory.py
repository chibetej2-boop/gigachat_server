# chat_memory.py
# ARKANUM MEMORY v3 (SUPABASE CONTROLLED)

from db import supabase


# ==========================================
# SETTINGS
# ==========================================

MAX_CONTEXT_MESSAGES = 30  # можно менять


# ==========================================
# SAVE MESSAGE
# ==========================================

def save_message(chat_id: str, role: str, content: str):

    supabase.table("chat_memory").insert({
        "chat_id": chat_id,
        "role": role,
        "content": content
    }).execute()


# ==========================================
# LOAD HISTORY (ORDERED + LIMITED)
# ==========================================

def load_history(chat_id: str):

    response = (
        supabase
        .table("chat_memory")
        .select("*")
        .eq("chat_id", chat_id)
        .order("created_at", desc=False)  # строго по времени создания
        .limit(200)  # берём максимум 200 из базы
        .execute()
    )

    data = response.data or []

    # Берём только последние N сообщений в контекст модели
    if len(data) > MAX_CONTEXT_MESSAGES:
        data = data[-MAX_CONTEXT_MESSAGES:]

    return data