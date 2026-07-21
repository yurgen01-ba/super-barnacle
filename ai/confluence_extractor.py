from __future__ import annotations

from ai.json_repair import safe_json_array_loads
from providers.text.factory import create_text_provider


def extract_confluence_knowledge(
    text: str,
    source: str = "confluence",
    provider_name: str = "ollama",
    model: str = "qwen2.5:7b",
    host: str = "http://localhost:11434",
    timeout_seconds: int = 180,
):
    """Extract Confluence knowledge using the configured local provider."""
    if not text or not text.strip():
        return []

    provider = create_text_provider(
        provider_name=provider_name,
        model=model,
        host=host,
        timeout_seconds=timeout_seconds,
    )
    prompt = f"""
You are a senior Business/System Analyst extracting project knowledge from a
Confluence page. Return ONLY a valid JSON array with type, title, content and
source. Allowed types: requirement, feature, business_rule, decision, risk,
question, assumption, integration, glossary. Preserve system names, APIs,
fields, roles, processes and decisions. Do not invent information. Prefer
5-15 concrete items. Use source "{source}". Return [] only for empty or
unreadable input.

CONFLUENCE TEXT:
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
