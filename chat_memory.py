# chat_memory.py
# ARKANUM ADVANCED PERSISTENT MEMORY v2
# PROFILE + HISTORY + STRUCTURED LONG-TERM MEMORY + SAFE COMPATIBILITY

import json
import os
import time
from typing import List, Dict, Optional


class ChatMemory:

    def __init__(self, chat_id: str):

        self.chat_id = chat_id

        # основной файл памяти
        self.file_path = f"memory_{chat_id}.json"

        # история сообщений (short-term memory)
        self.messages: List[Dict[str, str]] = []

        # профиль пользователя (structured memory)
        self.profile: Dict[str, str] = {}

        # долговременные факты (long-term memory layer)
        self.long_term_memory: Dict[str, Dict] = {}

        # мета
        self.meta: Dict[str, str] = {
            "created": str(time.time()),
            "last_update": str(time.time())
        }

        # загрузка
        self._load()


    # ==============================
    # LOAD FROM FILE
    # ==============================
    def _load(self):

        if not os.path.exists(self.file_path):
            return

        try:

            with open(self.file_path, "r", encoding="utf-8") as f:

                data = json.load(f)

                # backward compatibility
                self.messages = data.get("messages", [])

                self.profile = data.get("profile", {})

                self.long_term_memory = data.get("long_term_memory", {})

                self.meta = data.get("meta", self.meta)

        except Exception as e:

            print("MEMORY LOAD ERROR:", e)

            self.messages = []

            self.profile = {}

            self.long_term_memory = {}

            self.meta = {
                "created": str(time.time()),
                "last_update": str(time.time())
            }


    # ==============================
    # SAVE TO FILE
    # ==============================
    def _save(self):

        try:

            self.meta["last_update"] = str(time.time())

            with open(self.file_path, "w", encoding="utf-8") as f:

                json.dump({

                    "messages": self.messages,
                    "profile": self.profile,
                    "long_term_memory": self.long_term_memory,
                    "meta": self.meta

                }, f, ensure_ascii=False, indent=2)

        except Exception as e:

            print("MEMORY SAVE ERROR:", e)


    # ==============================
    # ADD USER MESSAGE
    # ==============================
    def add_user(self, text: str):

        self.messages.append({

            "role": "user",
            "content": text,
            "timestamp": time.time()

        })

        self._auto_extract_profile(text)

        self._extract_long_term_memory(text)

        self._trim_short_term()

        self._save()


    # ==============================
    # ADD ASSISTANT MESSAGE
    # ==============================
    def add_assistant(self, text: str):

        self.messages.append({

            "role": "assistant",
            "content": text,
            "timestamp": time.time()

        })

        self._trim_short_term()

        self._save()


    # ==============================
    # LIMIT SHORT TERM MEMORY SIZE
    # ==============================
    def _trim_short_term(self, max_messages: int = 100):

        if len(self.messages) > max_messages:

            self.messages = self.messages[-max_messages:]


    # ==============================
    # GET HISTORY (COMPATIBILITY)
    # ==============================
    def get_messages(self):

        return self.messages


    # ==============================
    # GET PROFILE
    # ==============================
    def get_profile(self):

        return self.profile


    # ==============================
    # GET LONG TERM MEMORY
    # ==============================
    def get_long_term_memory(self):

        return self.long_term_memory


    # ==============================
    # BUILD CONTEXT FOR AI (ENHANCED)
    # ==============================
    def build_context(self):

        context = []

        # PROFILE CONTEXT
        if self.profile:

            profile_text = "User profile:\n"

            for key, value in self.profile.items():

                profile_text += f"{key}: {value}\n"

            context.append({

                "role": "system",
                "content": profile_text

            })

        # LONG TERM MEMORY CONTEXT
        if self.long_term_memory:

            memory_text = "Long-term memory:\n"

            for key, value in self.long_term_memory.items():

                memory_text += f"{key}: {value.get('value')}\n"

            context.append({

                "role": "system",
                "content": memory_text

            })

        # SHORT TERM MEMORY
        context.extend(self.messages)

        return context


    # ==============================
    # AUTO PROFILE EXTRACTION
    # ==============================
    def _auto_extract_profile(self, text: str):

        text_lower = text.lower()

        if "меня зовут" in text_lower:

            name = text.split("меня зовут")[-1].strip()

            self.profile["name"] = name

        if "my name is" in text_lower:

            name = text.split("my name is")[-1].strip()

            self.profile["name"] = name

        if "мне нравится" in text_lower:

            interest = text.split("мне нравится")[-1].strip()

            self.profile["interest"] = interest

        if "i like" in text_lower:

            interest = text.split("i like")[-1].strip()

            self.profile["interest"] = interest

        if "я работаю" in text_lower:

            job = text.split("я работаю")[-1].strip()

            self.profile["job"] = job

        if "i work as" in text_lower:

            job = text.split("i work as")[-1].strip()

            self.profile["job"] = job


    # ==============================
    # LONG TERM MEMORY EXTRACTION
    # ==============================
    def _extract_long_term_memory(self, text: str):

        text_lower = text.lower()

        # имя
        if "меня зовут" in text_lower:

            name = text.split("меня зовут")[-1].strip()

            self._store_long_term("user_name", name)

        if "my name is" in text_lower:

            name = text.split("my name is")[-1].strip()

            self._store_long_term("user_name", name)

        # цели
        if "моя цель" in text_lower:

            goal = text.split("моя цель")[-1].strip()

            self._store_long_term("user_goal", goal)

        if "my goal is" in text_lower:

            goal = text.split("my goal is")[-1].strip()

            self._store_long_term("user_goal", goal)


    # ==============================
    # STORE LONG TERM MEMORY
    # ==============================
    def _store_long_term(self, key: str, value: str):

        self.long_term_memory[key] = {

            "value": value,
            "timestamp": time.time()

        }


    # ==============================
    # CLEAR MEMORY
    # ==============================
    def clear(self):

        self.messages = []

        self.profile = {}

        self.long_term_memory = {}

        self.meta = {
            "created": str(time.time()),
            "last_update": str(time.time())
        }

        self._save()