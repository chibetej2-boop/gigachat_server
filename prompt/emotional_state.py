# emotional_state.py
# ARKANUM EMOTIONAL STATE LAYER
# Управляет глубиной, настроением и фокусом диалога

class EmotionalState:

    def __init__(self):

        # базовые параметры
        self.mood = "neutral"
        self.depth = 0.5
        self.focus = "balanced"

    # ==========================
    # UPDATE FROM USER TEXT
    # ==========================
    def update_from_text(self, text: str):

        if not text:
            return

        text_lower = text.lower()

        # глубина
        deep_words = [
            "смысл",
            "зачем",
            "почему",
            "кто я",
            "предназначение",
            "истина",
            "реальность",
            "осознан",
            "существование"
        ]

        shallow_words = [
            "привет",
            "ок",
            "понятно",
            "да",
            "нет"
        ]

        # увеличиваем глубину
        if any(word in text_lower for word in deep_words):
            self.depth = min(1.0, self.depth + 0.1)

        # уменьшаем глубину
        elif any(word in text_lower for word in shallow_words):
            self.depth = max(0.2, self.depth - 0.05)

        # настроение
        if "?" in text:
            self.mood = "inquiry"

        elif any(word in text_lower for word in ["страх", "боюсь", "тревога"]):
            self.mood = "fragile"

        elif any(word in text_lower for word in ["рад", "счаст", "люблю"]):
            self.mood = "open"

        else:
            self.mood = "neutral"

        # фокус
        if self.depth > 0.75:
            self.focus = "existential"

        elif self.depth < 0.35:
            self.focus = "surface"

        else:
            self.focus = "balanced"


    # ==========================
    # BUILD CONTEXT FOR MODEL
    # ==========================
    def build_context(self):

        return {
            "role": "system",
            "content": (
                "Emotional modulation layer active.\n"
                f"Mood: {self.mood}\n"
                f"Depth: {self.depth:.2f}\n"
                f"Focus: {self.focus}\n"
                "Adjust response tone and depth accordingly."
            )
        }