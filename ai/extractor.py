from __future__ import annotations

from ai.json_repair import safe_json_array_loads
from providers.text.factory import create_text_provider


def extract_knowledge(
    text: str,
    source: str = "unknown",
    provider_name: str = "ollama",
    model: str = "qwen2.5:7b",
    host: str = "http://localhost:11434",
    timeout_seconds: int = 180,
):
    """Extract generic text knowledge using the configured local provider."""
    if not text or not text.strip():
        return []

    provider = create_text_provider(
        provider_name=provider_name,
        model=model,
        host=host,
        timeout_seconds=timeout_seconds,
    )
    prompt = f"""
You are a strict JSON knowledge extraction engine for a project memory system.
Return ONLY a valid JSON array with objects containing type, title, content and source.
Allowed types: decision, requirement, risk, feature, question, assumption,
business_rule, integration, glossary.
Do not invent information. Extract only concrete facts. Return at most 20 items.
Use source "{source}". Return [] when nothing useful is present.

TEXT:
{text[:12000]}
"""
    data = safe_json_array_loads(provider.generate(prompt))
    if not isinstance(data, list):
        return []
    return [
        {
            "type": str(item.get("type") or "unknown")[:80],
            "title": str(item.get("title") or "Untitled")[:220],
            "content": str(item.get("content") or "")[:1400],
            "source": str(item.get("source") or source),
        }
        for item in data
        if isinstance(item, dict) and str(item.get("content") or "").strip()
    ]
