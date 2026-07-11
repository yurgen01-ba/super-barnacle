from __future__ import annotations

from transcription.loop_cleaner import clean_asr_loops
from transcription.mixed_language_resolver import resolve_mixed_language_terms
from transcription.sentence_boundary_repair import repair_sentence_boundaries
from transcription.boundary_stitcher import stitch_segment_texts
from transcription.utterance_reconstruction import (
    assign_segments_to_speakers,
    render_utterance_transcript,
    serialize_utterances,
)

def clean_transcript_text(text: str) -> str:
    text=clean_asr_loops(text)
    text=resolve_mixed_language_terms(text)
    text=repair_sentence_boundaries(text)
    return text.strip()

def build_clean_transcript(transcript_segments:list[dict],speaker_turns:list|None=None)->dict:
    cleaned=[]
    for segment in transcript_segments:
        item=dict(segment)
        item["clean_text"]=clean_transcript_text(item.get("repaired_text") or item.get("raw_text") or "")
        item["repaired_text"]=item["clean_text"]
        cleaned.append(item)
    stitched=stitch_segment_texts([x.get("clean_text","") for x in cleaned])
    utterances=[]; speaker_text=""
    if speaker_turns:
        utterances=assign_segments_to_speakers(cleaned,speaker_turns)
        speaker_text=render_utterance_transcript(utterances)
    return {
        "clean_transcript":stitched,
        "speaker_transcript":speaker_text or stitched,
        "segments":cleaned,
        "utterances":serialize_utterances(utterances),
    }
