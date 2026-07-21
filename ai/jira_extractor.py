from __future__ import annotations

from ai.json_repair import safe_json_array_loads
from providers.text.factory import create_text_provider


def _normalize_items(data, source: str):
    if not isinstance(data, list):
        return []
    normalized = []
    for item in data:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title") or "Untitled").strip()
        content = str(item.get("content") or "").strip()
        if not content:
            continue
        normalized.append({
            "type": str(item.get("type") or "unknown")[:80],
            "title": title[:220],
            "content": content[:1400],
            "source": str(item.get("source") or source),
        })
    return normalized


def extract_jira_knowledge(
    text: str,
    source: str = "jira",
    provider_name: str = "ollama",
    model: str = "qwen2.5:7b",
    host: str = "http://localhost:11434",
    timeout_seconds: int = 180,
):
    """Extract Jira knowledge through the text provider selected in project settings."""
    if not text or not text.strip():
        return []

    provider = create_text_provider(
        provider_name=provider_name,
        model=model,
        host=host,
        timeout_seconds=timeout_seconds,
    )
    source_text = text[:12000]
    prompt = f"""
You are a senior Business/System Analyst extracting project knowledge from Jira issue export text.
The input may be noisy because it comes from a Jira PDF export.

Return ONLY a valid JSON array:
[
  {{
    "type": "requirement",
    "title": "short concrete title",
    "content": "specific useful Jira fact",
    "source": "{source}"
  }}
]

Allowed type values: requirement, feature, business_rule, decision, risk,
question, assumption, integration, glossary.

Rules:
- Do not invent information and do not add explanations or markdown.
- Preserve Jira IDs in titles and content.
- Extract acceptance criteria as requirements or business rules.
- Extract blockers and dependencies as risks.
- Extract unresolved clarifications as questions.
- Prefer 5-15 concrete items and avoid generic statements.
- Return [] only when the input is empty or unreadable.

JIRA TEXT:
{source_text}
"""
    response = provider.generate(prompt)
    return _normalize_items(safe_json_array_loads(response), source=source)
