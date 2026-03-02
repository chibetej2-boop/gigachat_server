class DialogueGovernor:

    def __init__(self):
        pass

    def build_governor_message(self, conversation):

        depth_level = self._detect_depth(conversation)
        tone_instruction = self._detect_tone(conversation)

        content = f"""
DIALOGUE REGULATION MODE:

1. Do not answer academically.
2. Do not give broad generalizations.
3. Speak as a living interlocutor.
4. Gradually deepen the topic.
5. First response — calm and simple.
6. Each next response — slightly deeper.
7. If referencing traditions, speak concretely:
   Example: "In one Zen tradition..." and then explain it specifically.
8. If imagining or hypothesizing — clearly separate:
   - factual knowledge
   - personal speculation

DEPTH LEVEL: {depth_level}
TONE MODE: {tone_instruction}
"""

        return {
            "role": "system",
            "content": content.strip()
        }

    def _detect_depth(self, conversation):
        message_count = len(conversation)

        if message_count < 3:
            return "introductory"
        elif message_count < 6:
            return "developing"
        else:
            return "deep exploration"

    def _detect_tone(self, conversation):
        last_user_message = ""
        for msg in reversed(conversation):
            if msg["role"] == "user":
                last_user_message = msg["content"].lower()
                break

        emotional_keywords = ["страх", "больно", "одиноч", "смысл", "пустот", "кризис"]

        for word in emotional_keywords:
            if word in last_user_message:
                return "intimate"

        return "neutral-thoughtful"