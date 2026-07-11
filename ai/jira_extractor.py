import json
import re

from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, CLAUDE_EXTRACTOR_MODEL


client = Anthropic(api_key=ANTHROPIC_API_KEY)


def _extract_json_array(text: str) -> str:
    cleaned = text.strip()

    cleaned = re.sub(
        r"^```(?:json)?",
        "",
        cleaned,
        flags=re.IGNORECASE,
    ).strip()

    cleaned = re.sub(r"```$", "", cleaned).strip()

    start = cleaned.find("[")
    end = cleaned.rfind("]")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(
            f"No JSON array found in model response. Preview: {cleaned[:500]}"
        )

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


def extract_jira_knowledge(text: str, source: str = "jira"):
    """
    Jira-specific extractor.

    Generic extraction can be too strict for Jira exports because PDF text may be noisy.
    This extractor is optimized for Jira issues, epics, user stories, acceptance criteria,
    descriptions, comments, statuses, priorities, blockers, and dependencies.
    """
    if not text or not text.strip():
        return []

    source_text = text[:16000]

    primary_prompt = f"""
You are a senior Business/System Analyst extracting project knowledge from Jira issue export text.

The input may be noisy because it comes from a Jira PDF export.
It may contain issue keys, titles, descriptions, comments, acceptance criteria, statuses, priorities, labels, assignees, dates, and formatting artifacts.

Return ONLY a valid JSON array:

[
  {{
    "type": "requirement",
    "title": "short concrete title",
    "content": "specific useful Jira fact",
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
- Extract concrete Jira facts even if text is noisy.
- Prefer issue key + issue title when available.
- Preserve Jira IDs like ABC-123, PAY-45, KYC-88 in title/content if present.
- Extract acceptance criteria as requirements or business_rules.
- Extract blockers/dependencies as risks.
- Extract unresolved clarifications as questions.
- Extract API/system/service mentions as integrations.
- Avoid generic items like "Jira contains tasks".
- If the text has Jira issues, return useful items.
- Return 5-20 items when possible.
- Keep source as "{source}".

JIRA TEXT:
{source_text}
"""

    data = _call_claude_json(primary_prompt)
    items = _normalize_items(data, source=source)

    if items:
        return items

    fallback_prompt = f"""
The previous extraction returned no items, but the text is from Jira and likely contains useful project information.

Extract practical project facts for a new analyst.

Return ONLY a valid JSON array:

[
  {{
    "type": "feature",
    "title": "short concrete title",
    "content": "specific fact from the Jira text",
    "source": "{source}"
  }}
]

Allowed type values:
- feature
- requirement
- business_rule
- risk
- question
- integration
- decision
- assumption
- glossary

Fallback rules:
- Do NOT return [] unless the text is completely empty or unreadable.
- If there are issue titles, extract them as feature/requirement.
- If there are descriptions, extract useful business or system behavior.
- If there are acceptance criteria, extract them as requirements/business_rules.
- If there are statuses, blockers, dependencies, errors, or failures, extract them as risks.
- If there are comments asking for clarification, extract questions.
- Keep facts grounded in the text.
- Return 5-15 items when possible.
- Keep source as "{source}".

JIRA TEXT:
{source_text}
"""

    fallback_data = _call_claude_json(fallback_prompt)
    return _normalize_items(fallback_data, source=source)

