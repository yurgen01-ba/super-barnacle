from __future__ import annotations

import re


def phrase_repetition_ratio(text: str) -> float:
    words = re.findall(r"[A-Za-zА-Яа-яЁёІіЇїЄєҐґ0-9]+", text or "")
    if len(words) < 4:
        return 0.0

    phrases = []
    lowered = [word.lower() for word in words]
    for size in (2, 3, 4):
        for index in range(0, len(lowered) - size + 1):
            phrases.append(" ".join(lowered[index:index + size]))

    if not phrases:
        return 0.0

    repeated = len(phrases) - len(set(phrases))
    return round(repeated / max(len(phrases), 1), 3)


def repeated_sentence_ratio(text: str) -> float:
    sentences = [s.strip().lower() for s in re.split(r"[.!?]+", text or "") if s.strip()]
    if len(sentences) < 2:
        return 0.0
    repeated = len(sentences) - len(set(sentences))
    return round(repeated / max(len(sentences), 1), 3)
