from __future__ import annotations
from ai.project_chat_v3 import answer_project_question_v3

def answer_project_question(question: str, *args, **kwargs) -> str:
    return answer_project_question_v3(question, *args, **kwargs)
