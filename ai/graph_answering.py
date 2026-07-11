from __future__ import annotations

from ai.graph_prompt_builder import build_graph_prompt
from graph.graph_retriever_v2 import GraphRetrieverV2


def answer_project_question_over_graph(
    question: str,
    text_provider=None,
    graph_retriever: GraphRetrieverV2 | None = None,
) -> str:
    graph_retriever = graph_retriever or GraphRetrieverV2()
    retrieved = graph_retriever.retrieve(question)

    prompt = build_graph_prompt(
        question=question,
        graph_context=retrieved.context,
    )

    if text_provider is None:
        text_provider = _get_default_text_provider()

    if text_provider is None:
        return _fallback_graph_answer(question, retrieved.context)

    for method_name in ["generate", "complete", "ask", "invoke"]:
        method = getattr(text_provider, method_name, None)
        if callable(method):
            try:
                return method(prompt)
            except TypeError:
                try:
                    return method(prompt=prompt)
                except Exception:
                    continue
            except Exception:
                continue

    return _fallback_graph_answer(question, retrieved.context)


def _get_default_text_provider():
    try:
        from providers.text.factory import get_text_provider
        return get_text_provider()
    except Exception:
        pass

    try:
        from providers.text.factory import create_text_provider
        return create_text_provider()
    except Exception:
        pass

    try:
        from providers.text.ollama_provider import OllamaTextProvider
        return OllamaTextProvider()
    except Exception:
        return None


def _fallback_graph_answer(question: str, graph_context: str) -> str:
    return (
        "Я не смог вызвать текстовую модель, но подготовил graph-first контекст.\\n\\n"
        f"Вопрос:\\n{question}\\n\\n"
        f"Контекст графа:\\n{graph_context}"
    )
