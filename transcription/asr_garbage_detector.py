from __future__ import annotations

import re
from dataclasses import dataclass


KNOWN_GARBAGE_PHRASES = {
    "ничего не помиделся",
    "тайкло",
    "финскопов",
    "застайск",
    "сигнал над здесь",
    "аж блю",
    "ajblue",
    "собушкой",
    "стаск",
}


@dataclass(slots=True)
class GarbageDetectionResult:
    score_penalty: float
    markers: list[str]
    suspicious_words: list[str]
    repeated_phrases: list[str]


def detect_repeated_phrases(text: str, min_words: int = 2) -> list[str]:
    words = re.findall(r"[A-Za-zА-Яа-яЁёІіЇїЄєҐґ0-9]+", text or "")
    lowered = [word.lower() for word in words]
    repeated = []

    for size in range(min_words, min(6, max(len(lowered), 1)) + 1):
        seen = {}
        for index in range(0, len(lowered) - size + 1):
            phrase = " ".join(lowered[index:index + size])
            seen[phrase] = seen.get(phrase, 0) + 1
        repeated.extend([phrase for phrase, count in seen.items() if count >= 2])

    return sorted(set(repeated))


def detect_suspicious_words(text: str) -> list[str]:
    words = re.findall(r"[A-Za-zА-Яа-яЁёІіЇїЄєҐґ0-9]{4,}", text or "")
    suspicious = []

    for word in words:
        lowered = word.lower()
        if lowered in KNOWN_GARBAGE_PHRASES:
            suspicious.append(word)
            continue
        if lowered.endswith(("скопов", "стайск", "айдлов", "иделся")):
            suspicious.append(word)
            continue
        if re.search(r"[bcdfghjklmnpqrstvwxyz]{5,}", lowered):
            suspicious.append(word)
            continue
        if re.search(r"[бвгджзйклмнпрстфхцчшщ]{5,}", lowered):
            suspicious.append(word)

    return sorted(set(suspicious))


def detect_asr_garbage(text: str) -> GarbageDetectionResult:
    lowered = (text or "").lower()
    markers = [phrase for phrase in KNOWN_GARBAGE_PHRASES if phrase in lowered]
    repeated = detect_repeated_phrases(text)
    suspicious = detect_suspicious_words(text)

    penalty = 0.0
    penalty += min(0.45, len(markers) * 0.18)
    penalty += min(0.35, len(repeated) * 0.08)
    penalty += min(0.25, len(suspicious) * 0.05)

    return GarbageDetectionResult(
        score_penalty=round(min(0.85, penalty), 3),
        markers=markers,
        suspicious_words=suspicious,
        repeated_phrases=repeated[:20],
    )
