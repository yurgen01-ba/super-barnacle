from __future__ import annotations

import re
from transcription.asr_garbage_detector import detect_asr_garbage
from transcription.repetition_detector import phrase_repetition_ratio, repeated_sentence_ratio
from transcription.unknown_word_detector import unknown_word_ratio
from dataclasses import dataclass


GARBAGE_MARKERS = [
    "эээ",
    "ммм",
    "неразборчиво",
    "за собушкой",
    "помиделся",
    "ajblue",
]


@dataclass(slots=True)
class TranscriptQuality:
    score: float
    label: str
    reasons: list[str]


def score_transcript_segment(text: str, language: str = "ru") -> TranscriptQuality:
    text = text or ""
    reasons = []
    score = 1.0
    asr_garbage = detect_asr_garbage(text)
    if asr_garbage.score_penalty:
        score -= asr_garbage.score_penalty
        reasons.append(
            "asr_garbage:"
            + ",".join(asr_garbage.markers[:5] or asr_garbage.suspicious_words[:5] or asr_garbage.repeated_phrases[:5])
        )

    words = re.findall(r"[A-Za-zА-Яа-яЁёІіЇїЄєҐґ0-9]{2,}", text)
    if len(words) < 6:
        score -= 0.35
        reasons.append("too_few_words")

    unique_ratio = len(set(w.lower() for w in words)) / max(len(words), 1)
    if len(words) >= 20 and unique_ratio < 0.35:
        score -= 0.25
        reasons.append("low_unique_word_ratio")

    garbage_hits = [marker for marker in GARBAGE_MARKERS if marker.lower() in text.lower()]
    if garbage_hits:
        score -= min(0.4, 0.12 * len(garbage_hits))
        reasons.append("garbage_markers:" + ",".join(garbage_hits))

    phrase_repeat_ratio = phrase_repetition_ratio(text)
    sentence_repeat_ratio = repeated_sentence_ratio(text)

    if phrase_repeat_ratio >= 0.18:
        score -= min(0.35, phrase_repeat_ratio)
        reasons.append(f"phrase_repetition:{phrase_repeat_ratio}")

    if sentence_repeat_ratio >= 0.25:
        score -= min(0.45, sentence_repeat_ratio)
        reasons.append(f"sentence_repetition:{sentence_repeat_ratio}")

    unknown_ratio, unknown_words = unknown_word_ratio(text)
    if unknown_ratio >= 0.08:
        score -= min(0.35, unknown_ratio * 2)
        reasons.append("unknown_words:" + ",".join(unknown_words[:8]))

    latin_ratio = sum(1 for ch in text if "a" <= ch.lower() <= "z") / max(len(text), 1)
    cyr_ratio = sum(1 for ch in text if "а" <= ch.lower() <= "я" or ch.lower() == "ё") / max(len(text), 1)
    if language == "ru" and latin_ratio > 0.35 and cyr_ratio < 0.2:
        score -= 0.25
        reasons.append("unexpected_latin_ratio_for_ru")

    score = max(0.0, min(1.0, score))
    if score >= 0.75:
        label = "good"
    elif score >= 0.55:
        label = "medium"
    else:
        label = "bad"

    return TranscriptQuality(score=round(score, 3), label=label, reasons=reasons)
