from __future__ import annotations


def build_diarization_status(audio_intelligence: dict | None) -> dict:
    payload = audio_intelligence or {}
    runtime = payload.get("runtime") or {}

    return {
        "completed": bool(runtime.get("diarization")),
        "speaker_count": int(runtime.get("speaker_count") or 0),
        "speaker_labels": runtime.get("speaker_labels") or [],
        "warnings": payload.get("warnings") or [],
    }
