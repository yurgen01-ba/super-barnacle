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
            "title": title[:200],
            "content": content[:1200],
            "source": str(item.get("source") or source),
        })

    return normalized


def _call_claude_json(prompt: str):
    response = client.messages.create(
        model=CLAUDE_EXTRACTOR_MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )

    return _safe_json_loads(response.content[0].text)


def extract_meeting_knowledge(text: str, source: str = "meeting"):
    """
    Meeting-specific extractor.

    Pass 1: BA/SA extraction.
    Pass 2 fallback: if pass 1 returns [], force extraction of project facts.
    """
    if not text or not text.strip():
        return []

    source_text = text[:16000]

    primary_prompt = f"""
You are a senior Business/System Analyst extracting project knowledge from a meeting transcript.

The transcript may be informal, messy, incomplete, multilingual, and conversational.
Your task is to extract useful project knowledge, not to summarize the meeting.

Return ONLY a valid JSON array in this exact format:

[
  {{
    "type": "decision",
    "title": "short concrete title",
    "content": "specific useful project information from the transcript",
    "source": "{source}"
  }}
]

Allowed type values:
- decision
- requirement
- risk
- feature
- question
- assumption
- business_rule
- integration
- glossary

Extraction rules:
- Return ONLY JSON. No markdown. No explanations.
- Do not invent facts.
- Extract implied project knowledge if it is reasonably clear from the discussion.
- Do not require perfect formal wording.
- If people discuss a task, feature, blocker, dependency, decision, risk, requirement, uncertainty, API, UI flow, business rule, or integration, extract it.
- Prefer concrete project details over generic summaries.
- Avoid items like "team discussed the project".
- Each content value must be specific and useful for a new analyst.
- If transcript contains useful discussion, return 3-15 items.
- If truly no useful project knowledge exists, return [].
- Keep source as "{source}".
- Output may be in the same language as the transcript.

TRANSCRIPT:
{source_text}
"""

    data = _call_claude_json(primary_prompt)
    items = _normalize_items(data, source=source)

    if items:
        return items

    # Fallback: less strict, optimized for informative transcripts where no formal
    # requirements/decisions are explicitly phrased.
    fallback_prompt = f"""
You are converting an informative meeting transcript into Project Memory facts.

The previous extraction returned no items, but the transcript may still contain useful project information.
Extract concrete facts that would help a new Business Analyst understand the project.

Return ONLY a valid JSON array:

[
  {{
    "type": "feature",
    "title": "short concrete title",
    "content": "specific fact from the transcript",
    "source": "{source}"
  }}
]

Allowed type values:
- feature
- requirement
- business_rule
- decision
- risk
- question
- assumption
- integration
- glossary

Important:
- Do NOT return [] unless the transcript is only small talk or completely empty.
- Extract concrete project facts even if they are not phrased as formal requirements.
- If the transcript explains how something works, extract it as feature/business_rule/integration.
- If the transcript mentions a problem, uncertainty, dependency, or blocker, extract it as risk/question.
- If the transcript mentions what should be done, extract it as requirement.
- Keep facts grounded in the transcript. Do not invent.
- Return 5-12 items if the transcript is informative.
- Output may be in the same language as the transcript.
- Keep source as "{source}".

TRANSCRIPT:
{source_text}
"""

    fallback_data = _call_claude_json(fallback_prompt)
    return _normalize_items(fallback_data, source=source)

