import json
import re

from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_EXTRACTOR_MODEL


client = Anthropic(api_key=ANTHROPIC_API_KEY)


def _extract_json_array(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()

    start = cleaned.find("[")
    end = cleaned.rfind("]")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"No JSON array found. Preview: {cleaned[:500]}")

    return cleaned[start:end + 1]


def _safe_json_loads(text: str):
    json_text = _extract_json_array(text)

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as first_error:
        repair_prompt = f"""
Repair this invalid JSON into a valid JSON array.

Rules:
- Return ONLY valid JSON.
- No markdown.
- Preserve meaning.
- If impossible, return [].

INVALID JSON:
{json_text}
"""

        repair_response = client.messages.create(
            model=CLAUDE_EXTRACTOR_MODEL,
            max_tokens=2500,
            messages=[{"role": "user", "content": repair_prompt}],
        )

        repaired = _extract_json_array(repair_response.content[0].text)

        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            raise ValueError(
                f"Invalid JSON and repair failed. Original error: {first_error}. "
                f"Response preview: {text[:1000]}"
            )


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


def _call_claude_json(prompt: str):
    response = client.messages.create(
        model=CLAUDE_EXTRACTOR_MODEL,
        max_tokens=3200,
        messages=[{"role": "user", "content": prompt}],
    )

    return _safe_json_loads(response.content[0].text)


def extract_confluence_knowledge(text: str, source: str = "confluence"):
    """
    Confluence-specific extractor.

    Works with pasted Confluence pages, exported page text, specs, meeting notes,
    decision logs, architecture pages, how-to docs, and requirements pages.
    """
    if not text or not text.strip():
        return []

    source_text = text[:16000]

    primary_prompt = f"""
You are a senior Business/System Analyst extracting project knowledge from a Confluence article.

The input may contain headings, tables copied as text, bullets, decision logs, requirements,
architecture descriptions, process descriptions, meeting notes, or implementation notes.

Return ONLY a valid JSON array:

[
  {{
    "type": "requirement",
    "title": "short concrete title",
    "content": "specific useful Confluence fact",
    "source": "{source}"
  }}
]

Allowed type values:
- requirement
- feature
- business_rule
- decision
- risk
- question
- assumption
- integration
- glossary

Extraction rules:
- Return ONLY JSON. No markdown. No explanations.
- Do not invent information.
- Extract concrete useful knowledge for a new analyst.
- Preserve names of systems, services, APIs, fields, roles, flows, statuses, and business entities.
- Extract decisions from decision logs.
- Extract process rules as business_rule.
- Extract unclear/open topics as question.
- Extract dependencies/blockers as risk.
- Extract service/API/system interactions as integration.
- Avoid generic items like "Confluence article describes the project".
- Return 5-20 items when possible.
- Keep source as "{source}".

CONFLUENCE ARTICLE:
{source_text}
"""

    data = _call_claude_json(primary_prompt)
    items = _normalize_items(data, source=source)

    if items:
        return items

    fallback_prompt = f"""
The previous extraction returned no items, but this text is from a Confluence article.

Extract practical project facts for Project Memory.

Return ONLY a valid JSON array:

[
  {{
    "type": "feature",
    "title": "short concrete title",
    "content": "specific fact from the Confluence article",
    "source": "{source}"
  }}
]

Rules:
- Do NOT return [] unless the text is completely empty or unreadable.
- If the article explains how something works, extract feature/business_rule/integration.
- If it describes what should be done, extract requirement.
- If it mentions uncertainty, extract question.
- If it mentions blocker/dependency/problem, extract risk.
- If it defines terms, extract glossary.
- Keep facts grounded in the text.
- Return 5-15 items when possible.
- Keep source as "{source}".

CONFLUENCE ARTICLE:
{source_text}
"""

    fallback_data = _call_claude_json(fallback_prompt)
    return _normalize_items(fallback_data, source=source)

