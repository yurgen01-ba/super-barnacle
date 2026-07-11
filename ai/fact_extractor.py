from ai.json_repair import safe_json_array_loads
from providers.text.factory import create_text_provider




def _safe_json_loads_or_empty(text: str):
    return safe_json_array_loads(text)


def _normalize_facts(data, source: str):
    if not isinstance(data, list):
        return []

    facts = []

    for item in data:
        if not isinstance(item, dict):
            continue

        subject = str(item.get("subject") or "").strip()
        predicate = str(item.get("predicate") or "").strip()
        obj = str(item.get("object") or "").strip()

        if not subject or not predicate or not obj:
            continue

        facts.append({
            "subject": subject[:240],
            "predicate": predicate[:160],
            "object": obj[:1200],
            "fact_type": str(item.get("fact_type") or item.get("type") or "unknown")[:80],
            "confidence": item.get("confidence", 0.7),
            "status": str(item.get("status") or "proposed")[:80],
            "evidence": item.get("evidence") or item.get("quote"),
            "source": item.get("source") or source,
            "metadata": item.get("metadata") or {},
        })

    return facts


def extract_canonical_facts(
    text: str,
    source: str,
    source_type: str = "unknown",
    model: str = "qwen2.5:7b",
    host: str = "http://localhost:11434",
    timeout_seconds: int = 240,
):
    """
    Universal Canonical Fact extractor.

    Converts any source text into subject-predicate-object facts.
    Works for meeting transcripts, Slack, Jira, Confluence, PDFs.
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
You are a Canonical Fact Extractor for a software project understanding system.

Convert the input text into MANY atomic subject-predicate-object facts.

Return ONLY a valid JSON array:
[
  {{
    "subject": "Merchant",
    "predicate": "can_have_status",
    "object": "Suspended",
    "fact_type": "business_rule",
    "confidence": 0.82,
    "status": "proposed",
    "evidence": "short quote or paraphrase from source",
    "source": "{source}"
  }}
]

Allowed fact_type:
- business_rule
- requirement
- decision
- risk
- question
- assumption
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
- role
- status
- workflow
- unknown

Allowed status:
- proposed
- confirmed
- superseded
- deprecated

Rules:
- Return ONLY JSON. No markdown.
- Do not invent facts.
- Extract granular atomic facts. Prefer many precise facts over few summaries.
- One relationship, assertion, field, status, rule, exception, actor responsibility, API detail, or data dependency = one fact.
- Prefer canonical subjects: Merchant, Advance, Funder, Underwriter, ISA, Syndicator, LoCi, RDMetr, Worksheet, Payment, Funding, Underwriting, etc.
- Predicates should be snake_case verbs or relations:
  - is_a
  - has_field
  - has_status
  - can_have_status
  - requires
  - approved_by
  - funded_by
  - created_by
  - depends_on
  - integrates_with
  - validates
  - cannot_exceed
  - happens_after
  - visible_when
  - hidden_when
  - uses
  - stores
  - produces
  - blocks
- For open questions, use subject + predicate like "needs_clarification".
- For risks, use predicate like "has_risk".
- For actions, use predicate like "needs_action".
- If source is informative, return 30-80 facts.
- If the same sentence contains 3 facts, split into 3 facts.
- Use confidence:
  - 0.9+ for explicit statements
  - 0.7-0.85 for clear paraphrases
  - 0.5-0.7 for assumptions/uncertain mentions
- Keep source exactly "{source}".
- Source type: {source_type}

INPUT:
{source_text}
"""

    response = provider.generate(prompt)
    facts = _normalize_facts(_safe_json_loads_or_empty(response), source=source)

    if len(facts) >= 10:
        return facts

    fallback_prompt = f"""
Extract atomic facts from this project text.

Return ONLY JSON array.
Each item must have:
subject, predicate, object, fact_type, confidence, status, evidence, source.

Extract 30-70 facts if possible.
Do not summarize. Split aggressively.
Do not invent facts.
Use source "{source}".

TEXT:
{source_text}
"""

    response = provider.generate(fallback_prompt)
    return _normalize_facts(_safe_json_loads_or_empty(response), source=source)

