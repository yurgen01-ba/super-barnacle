from __future__ import annotations

import re


DOMAIN_WORDS = {
    "jira", "confluence", "orgmeter", "bizcap", "equifax", "advance", "funder",
    "merchant", "underwriter", "syndicator", "referrer", "task", "ticket",
    "scope", "speaker", "problem", "info", "panel", "discount",
}

COMMON_RU_SHORT = {
    "это", "вот", "как", "если", "когда", "просто", "лучше", "делаем",
    "смотрели", "проблема", "описание", "задача", "показать", "вчера",
    "сегодня", "здесь", "там", "тебе", "короче",
}


def unknown_word_ratio(text: str) -> tuple[float, list[str]]:
    words = re.findall(r"[A-Za-zА-Яа-яЁёІіЇїЄєҐґ]{4,}", text or "")
    if not words:
        return 0.0, []

    unknown = []
    for word in words:
        w = word.lower()
        if w in DOMAIN_WORDS or w in COMMON_RU_SHORT:
            continue

        has_cyr = bool(re.search(r"[а-яё]", w))
        has_lat = bool(re.search(r"[a-z]", w))
        mixed = has_cyr and has_lat
        weird_endings = w.endswith(("скопов", "стайск", "айдлов", "иделся"))
        too_many_same = bool(re.search(r"(.)\1\1", w))

        if mixed or weird_endings or too_many_same:
            unknown.append(word)

    return round(len(unknown) / max(len(words), 1), 3), sorted(set(unknown))
