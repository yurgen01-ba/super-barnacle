from __future__ import annotations

import re

from ai.orgmeter_glossary import contains_orgmeter_domain_terms, repair_orgmeter_terms


GARBAGE_PATTERNS = [
    r"^[\W_]+$",
    r"\b(непонятно|неразборчиво|шум|music|silence)\b",
]

MIN_FACT_TEXT_LENGTH = 12


def normalize_fact_item(item: dict) -> dict:
    normalized = dict(item or {})

    for key in ["subject", "predicate", "object", "title", "content", "description", "text"]:
        if key in normalized and normalized[key] is not None:
            normalized[key] = repair_orgmeter_terms(str(normalized[key]))

    return normalized


def fact_text(item: dict) -> str:
    return " ".join(
        str(item.get(key) or "")
        for key in ["subject", "predicate", "object", "title", "content", "description", "text"]
    ).strip()


def is_quality_fact(item: dict) -> bool:
    text = fact_text(item)
    if len(text) < MIN_FACT_TEXT_LENGTH:
        return False

    for pattern in GARBAGE_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return False

    words = re.findall(r"[A-Za-zА-Яа-яЁёІіЇїЄєҐґ0-9]{2,}", text)
    if len(words) < 4:
        return False

    # Keep OrgMeter domain facts. For generic facts, require more substance.
    if contains_orgmeter_domain_terms(text):
        return True

    return len(words) >= 7


def filter_quality_facts(items: list[dict]) -> list[dict]:
    result = []
    seen = set()

    for item in items or []:
        if not isinstance(item, dict):
            continue

        normalized = normalize_fact_item(item)
        if not is_quality_fact(normalized):
            continue

        signature = fact_text(normalized).lower()
        if signature in seen:
            continue

        seen.add(signature)
        result.append(normalized)

    return result
