from __future__ import annotations
from transcription.audio_intelligence_service import audio_intelligence_service

def process_audio_with_selected_backend(
    audio_path: str,
    language: str | None = None,
    min_speakers: int | None = 2,
    max_speakers: int | None = 6,
    progress_callback=None,
    **processing_options,
) -> dict:
    if progress_callback: progress_callback({"event":"audio_intelligence_started","language":language})
    result=audio_intelligence_service.process(
        audio_path, language, min_speakers, max_speakers, **processing_options
    )
    if progress_callback: progress_callback({"event":"audio_intelligence_completed","backend":result.get("backend"),"model":result.get("model"),"segments":len(result.get("segments") or []),"warnings":result.get("warnings") or [],"runtime":result.get("runtime") or {}})
    return result
