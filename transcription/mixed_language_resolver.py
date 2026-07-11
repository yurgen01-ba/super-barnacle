from __future__ import annotations
import re
from difflib import SequenceMatcher

ALIASES={
"white label":{"вайт лейбл","вайтлейбл","вайт лейбер","байт лейбл","байтлэйбер"},
"Jira task":{"джира таск","джировский таск","жира таск","застайск"},
"info panel":{"инфо панель","инфопанель","инфо пэнел"},
"field scope":{"филд скоуп","финскоп","финскопов"},
"Save":{"сейв","сэйв","сэйдээ","сейдээ"},
"production":{"продакшн","продакшен"},
}

def _norm(s:str)->str:
    return re.sub(r"\s+"," ",re.sub(r"[^a-zа-я0-9\s]+"," ",s.lower().replace("ё","е"))).strip()

def resolve_mixed_language_terms(text: str, threshold: float = 0.78) -> str:
    resolved=text or ""
    for canonical, aliases in ALIASES.items():
        for alias in sorted(aliases,key=len,reverse=True):
            resolved=re.sub(re.escape(alias),canonical,resolved,flags=re.I)
    words=resolved.split()
    for size in (3,2,1):
        i=0
        while i<=len(words)-size:
            phrase=" ".join(words[i:i+size]); best=None; score=0.0
            for canonical, aliases in ALIASES.items():
                for alias in aliases:
                    r=SequenceMatcher(None,_norm(phrase),_norm(alias)).ratio()
                    if r>score: best,score=canonical,r
            if best and score>=threshold:
                words[i:i+size]=[best]
            i+=1
    return " ".join(words)
