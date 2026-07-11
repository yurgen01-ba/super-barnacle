from __future__ import annotations
from reasoning.reasoning_pipeline import reasoning_pipeline

def answer_project_question_v3(question: str, text_provider=None, project_id: str = "default") -> str:
    context=reasoning_pipeline.build_context(question, project_id=project_id)
    prompt=build_project_chat_v3_prompt(question, context["prompt_context"])
    if text_provider is None: text_provider=_get_default_text_provider()
    if text_provider is None: return context["prompt_context"]
    for name in ["generate","complete","ask","invoke"]:
        method=getattr(text_provider,name,None)
        if callable(method):
            try: return method(prompt)
            except TypeError:
                try: return method(prompt=prompt)
                except Exception: continue
            except Exception: continue
    return context["prompt_context"]

def build_project_chat_v3_prompt(question: str, reasoning_context: str) -> str:
    return f"""
You are Project Brain AI Analyst.
Use only the structured Knowledge OS context below.
Rules:
- Answer in the same language as the user's question.
- Use Project Model first.
- Use ranked evidence only to support the answer.
- Do not invent unknown actors, processes, entities or statuses.
- Use canonical terms: Advance = "кредит / Advance", not "аванс"; Merchant = "мерчант / заемщик"; Funder = "кредитор / funder".
- If something is not confidently extracted, say so.

KNOWLEDGE OS CONTEXT:
{reasoning_context}

USER QUESTION:
{question}

ANSWER:
""".strip()

def _get_default_text_provider():
    try:
        from providers.text.factory import get_text_provider
        return get_text_provider()
    except Exception: pass
    try:
        from providers.text.factory import create_text_provider
        return create_text_provider()
    except Exception: pass
    try:
        from providers.text.ollama_provider import OllamaTextProvider
        return OllamaTextProvider()
    except Exception: return None
