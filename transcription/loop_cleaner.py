from __future__ import annotations
import re

def collapse_character_loops(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"([А-Яа-яЁёA-Za-z])\1{2,}", r"\1\1", text)
    text = re.sub(r"\b[эеауыяюё]{6,}\b", "[неразборчиво]", text, flags=re.I)
    return text

def collapse_repeated_words(text: str, max_consecutive: int = 3) -> str:
    words = (text or "").split()
    out, prev, count = [], None, 0
    for word in words:
        norm = re.sub(r"[^\w]+", "", word.lower())
        if norm == prev and norm:
            count += 1
        else:
            prev, count = norm, 1
        if count <= max_consecutive:
            out.append(word)
        elif count == max_consecutive + 1:
            out.append(f"[повтор '{norm}' удалён]")
    return " ".join(out)

def clean_asr_loops(text: str) -> str:
    return re.sub(r"\s+", " ", collapse_repeated_words(collapse_character_loops(text))).strip()
