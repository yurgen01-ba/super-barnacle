from __future__ import annotations
from transcription.audio_contracts import TranscriptSegment

def ts(seconds:float)->str:
    seconds=max(float(seconds or 0),0); minutes,sec=divmod(seconds,60); hours,minutes=divmod(int(minutes),60)
    return f"{hours:02d}:{minutes:02d}:{sec:06.3f}"

def merge(segments:list[TranscriptSegment],max_gap_seconds:float=1.25)->list[TranscriptSegment]:
    if not segments:return []
    out=[segments[0]]
    for cur in segments[1:]:
        prev=out[-1]
        if prev.speaker and cur.speaker and prev.speaker==cur.speaker and cur.start-prev.end<=max_gap_seconds:
            prev.end=max(prev.end,cur.end); prev.text=(prev.text+" "+cur.text).strip(); prev.words.extend(cur.words)
        else: out.append(cur)
    return out

def render_speaker_transcript(segments:list[TranscriptSegment])->str:
    return "\n\n".join(f"[{ts(s.start)}–{ts(s.end)}] {s.speaker or 'SPEAKER_UNKNOWN'}:\n{s.text}" for s in merge(segments))
