# chat_memory.py
# ARKANUM MEMORY v4 (SAFE SUPABASE MODE)

from db import supabase
import traceback


# ==========================================
# SETTINGS
# ==========================================

MAX_CONTEXT_MESSAGES = 30


# ==========================================
# SAVE MESSAGE (SAFE)
# ==========================================

def save_message(chat_id: str, role: str, content: str):

    try:
        supabase.table("chat_memory").insert({
            "chat_id": chat_id,
            "role": role,
            "content": content
        }).execute()

    except Exception as e:
        print("=== SUPABASE SAVE ERROR ===")
        print(str(e))
        traceback.print_exc()


# ==========================================
# LOAD HISTORY (SAFE)
# ==========================================

def load_history(chat_id: str):

    try:
        response = (
            supabase
            .table("chat_memory")
            .select("*")
            .eq("chat_id", chat_id)
            .order("created_at", desc=False)
            .limit(200)
            .execute()
        )

        data = response.data or []

        if len(data) > MAX_CONTEXT_MESSAGES:
            data = data[-MAX_CONTEXT_MESSAGES:]

        return data

    except Exception as e:
        print("=== SUPABASE LOAD ERROR ===")
        print(str(e))
        traceback.print_exc()

        # Если Supabase упал — продолжаем без памяти
        return []