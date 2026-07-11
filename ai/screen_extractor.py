import base64
import json
import re
from pathlib import Path
from typing import List

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


def _image_to_base64(path: str) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode("utf-8")


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
            "type": str(item.get("type") or "screen_observation")[:80],
            "title": title[:220],
            "content": content[:1400],
            "source": str(item.get("source") or source),
        })

    return normalized


def analyze_screen_frames(
    frame_paths: List[str],
    source: str = "meeting_screen",
    batch_size: int = 4,
):
    """
    Analyze extracted video frames using a vision-capable Claude model.

    Returns extracted knowledge items from what is visible on screen:
    - Jira screens
    - Confluence pages
    - Figma/UI screens
    - diagrams
    - IDE/code
    - terminal/errors
    - Swagger/API docs
    - tables/forms
    """
    if not frame_paths:
        return []

    all_items = []

    for batch_start in range(0, len(frame_paths), batch_size):
        batch = frame_paths[batch_start:batch_start + batch_size]
        frame_numbers = list(range(batch_start + 1, batch_start + 1 + len(batch)))

        prompt = f"""
You are a visual project knowledge extractor.

You will receive screenshots extracted from a meeting video.
Analyze what is visible on screen and extract useful project knowledge.

Return ONLY a valid JSON array:

[
  {{
    "type": "screen_observation",
    "title": "short concrete title",
    "content": "specific useful information visible on screen",
    "source": "{source}:frame_1"
  }}
]

Allowed type values:
- screen_observation
- requirement
- feature
- business_rule
- risk
- question
- integration
- api
- ui_screen
- diagram
- error
- glossary

What to extract:
- Jira issue titles, statuses, acceptance criteria, comments, priorities
- Confluence headings, requirements, tables, decisions
- UI fields, buttons, validation, flows, screens
- diagrams, systems, dependencies, arrows, data flow
- API endpoints, payload fields, Swagger/OpenAPI info
- terminal errors, stack traces, failed commands
- code structure if visible
- important labels, statuses, entities, business terms

Rules:
- Do not invent details.
- Extract only what is visible or strongly implied by the screenshot.
- If screen is unreadable or irrelevant, return [] for that frame.
- Preserve visible text when important.
- Return 1-5 items per useful frame.
- Include frame number in source, e.g. "{source}:frame_3".
- Return ONLY JSON. No markdown.

Frame numbers in this batch:
{frame_numbers}
"""

        content = [{"type": "text", "text": prompt}]

        for path in batch:
            content.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": _image_to_base64(path),
                },
            })

        response = client.messages.create(
            model=CLAUDE_EXTRACTOR_MODEL,
            max_tokens=3000,
            messages=[{"role": "user", "content": content}],
        )

        data = _safe_json_loads(response.content[0].text)
        all_items.extend(_normalize_items(data, source=source))

    return all_items

