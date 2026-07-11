from __future__ import annotations

from config import AUDIO_TRANSCRIPTION_BACKEND


def create_audio_transcriber():
    backend = (AUDIO_TRANSCRIPTION_BACKEND or "whisperx").lower()

    if backend == "whisperx":
        try:
            from transcription.whisperx_transcriber import WhisperXTranscriber
            return WhisperXTranscriber()
        except Exception as exc:
            from transcription.openai_whisper_adapter import OpenAIWhisperAdapter
            adapter = OpenAIWhisperAdapter()
            adapter.startup_warning = (
                "WhisperX backend could not be initialized; "
                f"legacy OpenAI Whisper fallback is active: {exc!r}"
            )
            return adapter

    if backend == "openai-whisper":
        from transcription.openai_whisper_adapter import OpenAIWhisperAdapter
        return OpenAIWhisperAdapter()

    raise ValueError(f"Unsupported audio transcription backend: {backend}")
