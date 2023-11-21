import os
from typing import List


def promt_function(user_text: str, history: List[str], context: List[str]):
    system_prompt = (
        "Please respond to the user's question based on the dialogue history (history) and references (context) provided by the assistant.Notices:\n\n "
        + os.getenv("SYSTEM_PROMPT", "")
    )
    assistant_prompt = {"history": history, "context": context}

    user_prompt = user_text

    return [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": str(assistant_prompt)},
        {"role": "user", "content": user_prompt},
    ]


class ChatPrompt:
    @classmethod
    def get_message(self, user_text: str, history: List[str], context: List[str]):
        message = promt_function(user_text=user_text, history=history, context=context)
        return message
