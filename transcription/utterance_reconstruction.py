from __future__ import annotations
from dataclasses import dataclass, asdict

@dataclass(slots=True)
class Utterance:
    speaker:str
    start:float
    end:float
    text:str
    confidence:float|None=None

def _overlap(a1,a2,b1,b2): return max(0.0,min(a2,b2)-max(a1,b1))

def assign_segments_to_speakers(segments:list[dict],turns:list)->list[Utterance]:
    result=[]
    for s in segments:
        start=float(s.get("start_seconds") or 0); end=float(s.get("end_seconds") or start)
        text=(s.get("repaired_text") or s.get("text") or s.get("raw_text") or "").strip()
        if not text: continue
        speaker="SPEAKER_UNKNOWN"; best=0.0
        for t in turns:
            ts=float(getattr(t,"start",0)); te=float(getattr(t,"end",0))
            ov=_overlap(start,end,ts,te)
            if ov>best: best=ov; speaker=str(getattr(t,"speaker","SPEAKER_UNKNOWN"))
        q=s.get("quality") or {}; conf=float(q["score"]) if q.get("score") is not None else None
        result.append(Utterance(speaker,start,end,text,conf))
    return merge_adjacent_utterances(result)

def merge_adjacent_utterances(items:list[Utterance],max_gap_seconds:float=1.5)->list[Utterance]:
    if not items: return []
    out=[items[0]]
    for cur in items[1:]:
        prev=out[-1]
        if prev.speaker==cur.speaker and cur.start-prev.end<=max_gap_seconds:
            prev.end=max(prev.end,cur.end); prev.text=(prev.text+" "+cur.text).strip()
        else: out.append(cur)
    return out

def render_utterance_transcript(items:list[Utterance])->str:
    return "\n\n".join(f"[{u.start:08.2f}–{u.end:08.2f}] {u.speaker}: {u.text}" for u in items)

def serialize_utterances(items:list[Utterance])->list[dict]:
    return [asdict(x) for x in items]
