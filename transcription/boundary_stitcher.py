from __future__ import annotations
import re
from difflib import SequenceMatcher

def _tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-zА-Яа-яЁёІіЇїЄєҐґ0-9]+", (text or "").lower())

def remove_boundary_duplicate(previous: str, current: str, max_words: int = 80, threshold: float = 0.82) -> str:
    a, b = _tokens(previous), _tokens(current)
    max_size = min(max_words, len(a), len(b))
    for size in range(max_size, 3, -1):
        if SequenceMatcher(None, a[-size:], b[:size]).ratio() >= threshold:
            return " ".join(current.split()[size:]).strip()
    return current

def stitch_segment_texts(items: list[str]) -> str:
    out=[]
    for text in items:
        text=(text or "").strip()
        if not text: continue
        if out: text=remove_boundary_duplicate(out[-1],text)
        if text: out.append(text)
    return "\n\n".join(out)
