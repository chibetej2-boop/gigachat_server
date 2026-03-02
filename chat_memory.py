# chat_memory.py
# ARKANUM MEMORY v5 (MULTI-CHAT MODE)

from db import supabase
import traceback
import uuid
from datetime import datetime


# ==========================================
# SETTINGS
# ==========================================

MAX_CONTEXT_MESSAGES = 30


# ==========================================
# CREATE CHAT
# ==========================================

def create_chat(title: str = "New Chat") -> str:
    try:
        chat_id = str(uuid.uuid4())

        supabase.table("chats").insert({
            "chat_id": chat_id,
            "title": title,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

        return chat_id

    except Exception as e:
        print("=== CREATE CHAT ERROR ===")
        print(str(e))
        traceback.print_exc()
        return None


# ==========================================
# GET ALL CHATS
# ==========================================

def get_all_chats():
    try:
        response = (
            supabase
            .table("chats")
            .select("*")
            .order("created_at", desc=True)
            .execute()
        )

        return response.data or []

    except Exception as e:
        print("=== GET CHATS ERROR ===")
        print(str(e))
        traceback.print_exc()
        return []


# ==========================================
# DELETE CHAT
# ==========================================

def delete_chat(chat_id: str):
    try:
        supabase.table("chat_memory").delete().eq("chat_id", chat_id).execute()
        supabase.table("chats").delete().eq("chat_id", chat_id).execute()

    except Exception as e:
        print("=== DELETE CHAT ERROR ===")
        print(str(e))
        traceback.print_exc()


# ==========================================
# SAVE MESSAGE
# ==========================================

def save_message(chat_id: str, role: str, content: str):

    try:
        supabase.table("chat_memory").insert({
            "chat_id": chat_id,
            "role": role,
            "content": content,
            "created_at": datetime.utcnow().isoformat()
        }).execute()

    except Exception as e:
        print("=== SUPABASE SAVE ERROR ===")
        print(str(e))
        traceback.print_exc()


# ==========================================
# LOAD HISTORY
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
        return []