from __future__ import annotations

from providers.text.factory import create_text_provider


def repair_transcript_with_llm(
    text: str,
    model: str = "qwen2.5:7b",
    host: str = "http://localhost:11434",
    timeout_seconds: int = 180,
) -> str:
    """
    Conservative transcript repair.

    Rules:
    - fix obvious ASR mistakes, punctuation and domain terms;
    - do not summarize;
    - do not add new facts;
    - preserve meaning and speaker/timestamp markers.
    """
    if not text or not text.strip():
        return ""

    provider = create_text_provider(
        provider_name="ollama",
        model=model,
        host=host,
        timeout_seconds=timeout_seconds,
    )

    prompt = f"""
Ты исправляешь транскрипт встречи.

Правила:
- НЕ пересказывай.
- НЕ добавляй новые факты.
- НЕ удаляй смысловые фразы.
- Исправь только явные ошибки распознавания, пунктуацию и термины.
- Сохрани маркеры сегментов вида [Segment ...].
- Термины: Jira, Confluence, OrgMeter, Bizcap, Equifax, Advance, Funder, Merchant, Underwriter, Syndicator, Referrer, task, ticket, scope, problem, info panel.

ТЕКСТ:
{text[:12000]}
"""

    try:
        repaired = provider.generate(prompt)
        return repaired.strip() or text
    except Exception:
        return text
