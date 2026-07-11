from __future__ import annotations
import re

STARTERS = {"а","и","но","или","если","чтобы","когда","потому","что","как","то","например","типа","короче"}

def repair_sentence_boundaries(text: str) -> str:
    parts = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", text or "").strip())
    if len(parts) < 2:
        return text or ""
    result, buf = [], ""
    for part in parts:
        part = part.strip()
        if not part:
            continue
        words = part.split()
        first = words[0].lower().strip(".,!?") if words else ""
        if not buf:
            buf = part
        elif len(words) <= 4 or first in STARTERS:
            buf = buf.rstrip(".!?") + ", " + part[:1].lower() + part[1:]
        else:
            result.append(buf)
            buf = part
    if buf:
        result.append(buf)
    return " ".join(result).strip()
