from ai.json_repair import safe_json_array_loads
from providers.text.factory import create_text_provider




def _safe_json_loads_or_empty(text: str):
    return safe_json_array_loads(text)


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
            "content": content[:1800],
            "source": str(item.get("source") or source),
        })

    return normalized


def extract_meeting_knowledge_local(
    text: str,
    source: str = "meeting",
    model: str = "qwen2.5:7b",
    host: str = "http://localhost:11434",
    timeout_seconds: int = 240,
):
    """
    Dense extractor.

    Previous extractor was too conservative and produced too few items.
    This version intentionally extracts more granular facts:
    - requirements
    - decisions
    - risks
    - questions
    - business rules
    - integrations
    - UI/API/data details
    - tasks/action items
    - assumptions
    """
    if not text or not text.strip():
        return []

    provider = create_text_provider(
        provider_name="ollama",
        model=model,
        host=host,
        timeout_seconds=timeout_seconds,
    )

    source_text = text[:9000]

    prompt = f"""
You are a very meticulous Senior Business Analyst and System Analyst.

Your job is to extract MANY granular project knowledge items from a meeting transcript.

Return ONLY a valid JSON array:
[
  {{
    "type": "requirement",
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
- action_item
- api
- ui_screen
- data_model
- process
- constraint
- dependency
- bug

CRITICAL EXTRACTION RULES:
- Return ONLY JSON. No markdown.
- Do not invent facts.
- Extract granular items, not broad summaries. Prefer many small items over few large items.
- One distinct fact, rule, field, status, actor action, exception, or open question = one item.
- Do NOT merge unrelated requirements into one item.
- Extract even small facts if they may help a future analyst. Do not discard implementation details.
- Extract open questions and unclear points.
- Extract implied tasks/action items if people discuss what needs to be done.
- Extract system names, fields, statuses, roles, APIs, screens, flows, integrations, errors, constraints.
- Extract disagreements, doubts, blockers, dependencies.
- Extract business rules and edge cases.
- Extract UI details and acceptance criteria if mentioned.
- Extract data/model/entity details if mentioned.
- If transcript is informative, return 20-60 items per chunk. Extract densely.
- If only small talk, return [].
- Keep source exactly "{source}".
- Output can be in the transcript language.

BAD:
[
  {{"type": "feature", "title": "Project discussion", "content": "Team discussed the project"}}
]

GOOD:
[
  {{"type": "business_rule", "title": "Defaulted advances allocate voluntary payback to fees first", "content": "For defaulted advances, voluntary payback payments should be allocated to arrears first and then fees.", "source": "{source}"}},
  {{"type": "question", "title": "Clarify whether bounce fees are visible in Participation Payout History", "content": "The discussion suggests uncertainty about whether bounce fee allocation should appear in Participation Payout History.", "source": "{source}"}}
]

TRANSCRIPT:
{source_text}
"""

    response = provider.generate(prompt)
    items = _normalize_items(_safe_json_loads_or_empty(response), source=source)

    if len(items) >= 8:
        return items

    # Second pass: force recovery from conservative responses.
    fallback_prompt = f"""
The previous extraction was too conservative.

Extract a dense list of concrete project facts from this transcript.
Return ONLY valid JSON array. No markdown.

Types:
decision, requirement, risk, feature, question, assumption, business_rule, integration,
glossary, action_item, api, ui_screen, data_model, process, constraint, dependency, bug

Rules:
- Do not summarize the meeting.
- Extract 20-50 separate facts if possible.
- Split facts aggressively.
- Include uncertain items as question/assumption.
- Keep source "{source}".
- Do not invent facts.

TRANSCRIPT:
{source_text}
"""

    response = provider.generate(fallback_prompt)
    return _normalize_items(_safe_json_loads_or_empty(response), source=source)

