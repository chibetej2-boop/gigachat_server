# dialogue_governor.py
# DEEP DIALOGUE GOVERNOR (FRAGMENT MODE)

from typing import List, Dict


class DialogueGovernor:

    def __init__(self):
        pass

    def build_governor_message(self, conversation: List[Dict]) -> Dict[str, str]:

        last_user_message = self._get_last_user_message(conversation)
        depth_level = self._detect_depth(conversation)

        regulation = f"""
CORE RULE:

You are not allowed to provide full explanations.
You are not allowed to summarize a tradition.
You are not allowed to expand the topic broadly.

FRAGMENT RULE:

In each response:
1. Reveal only ONE concrete element:
   - one historical episode
   - one specific practice
   - one documented case
   - one short story from a known tradition

2. Do NOT add background overview.
3. Do NOT add general definitions.
4. Do NOT add structured explanations.
5. Maximum 5–6 sentences.

DIALOGUE RULE:

After revealing one fragment,
you MUST return the focus to the user.

You must:
- Ask why this interests them.
- Or ask what exactly they are looking for.
- Or gently test their intention.

The goal is not to explain the topic.
The goal is to discover the reason behind the question.

If you begin writing like a textbook —
you are violating the rules.

DEPTH LEVEL: {depth_level}
"""

        return {
            "role": "system",
            "content": regulation.strip()
        }

    def _get_last_user_message(self, conversation: List[Dict]) -> str:
        for msg in reversed(conversation):
            if msg["role"] == "user":
                return msg["content"].lower()
        return ""

    def _detect_depth(self, conversation: List[Dict]) -> str:
        message_count = len(conversation)

        if message_count < 4:
            return "entry"
        elif message_count < 8:
            return "exploration"
        else:
            return "deep investigation"