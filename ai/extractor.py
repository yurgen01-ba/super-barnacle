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
        raise ValueError(f"No JSON array found. Response preview: {cleaned[:500]}")

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


def extract_knowledge(text: str, source: str = "unknown"):
    if not text or not text.strip():
        return []

    source_text = text[:12000]

    prompt = f"""
You are a strict JSON knowledge extraction engine for an AI project memory system.

Extract structured knowledge from the input text.

Return ONLY a valid JSON array in this exact format:

[
  {{
    "type": "decision",
    "title": "short concrete title",
    "content": "specific fact from the source text",
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

Strict rules:
- Return ONLY JSON. No markdown. No explanations.
- Do not invent information.
- Extract ONLY concrete facts explicitly present in the text.
- Avoid generic items like "project has requirements".
- Each content value must be short, ideally under 350 characters.
- Escape all quotes correctly.
- If nothing useful is found, return [].
- Maximum 20 items.
- Keep source as "{source}".

TEXT:
{source_text}
"""

    response = client.messages.create(
        model=CLAUDE_EXTRACTOR_MODEL,
        max_tokens=2500,
        messages=[{"role": "user", "content": prompt}],
    )

    data = _safe_json_loads(response.content[0].text)

    if not isinstance(data, list):
        return []

    normalized = []
    for item in data:
        if not isinstance(item, dict):
            continue

        normalized.append({
            "type": str(item.get("type") or "unknown"),
            "title": str(item.get("title") or "Untitled")[:200],
            "content": str(item.get("content") or "")[:1200],
            "source": str(item.get("source") or source),
        })

    return normalized

