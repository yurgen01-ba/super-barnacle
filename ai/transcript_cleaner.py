from __future__ import annotations

import re

from ai.orgmeter_glossary import repair_orgmeter_terms


FILLER_PATTERNS = [
    r"\bээ+\b",
    r"\bэм+\b",
    r"\bмм+\b",
    r"\bугу\b",
    r"\bну\s+как\s+бы\b",
    r"\bкак\s+бы\b",
    r"\bкороче\b",
    r"\bтипа\b",
    r"\bвот\b",
]

REPEATED_WORD_PATTERN = re.compile(r"\b(\w{3,})(\s+\1\b)+", flags=re.IGNORECASE)


def clean_transcript_text(text: str) -> str:
    if not text:
        return ""

    cleaned = str(text)

    for pattern in FILLER_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)

    cleaned = REPEATED_WORD_PATTERN.sub(r"\1", cleaned)
    cleaned = repair_orgmeter_terms(cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"\s+([,.!?;:])", r"\1", cleaned)
    cleaned = cleaned.strip()

    return cleaned


def is_low_value_transcript(text: str) -> bool:
    cleaned = clean_transcript_text(text)
    if len(cleaned) < 20:
        return True

    words = re.findall(r"[A-Za-zА-Яа-яЁёІіЇїЄєҐґ0-9]{2,}", cleaned)
    if len(words) < 5:
        return True

    unique_ratio = len(set(w.lower() for w in words)) / max(len(words), 1)
    if len(words) > 20 and unique_ratio < 0.25:
        return True

    return False
