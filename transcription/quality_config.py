from __future__ import annotations

from dataclasses import dataclass
import os


@dataclass(frozen=True, slots=True)
class WhisperQualityConfig:
    language: str | None = None
    beam_size: int = 3
    best_of: int = 3
    temperature: float = 0.0
    condition_on_previous_text: bool = True
    compression_ratio_threshold: float = 2.4
    logprob_threshold: float = -1.0
    no_speech_threshold: float = 0.6
    fp16: bool = True


def get_default_language(language: str | None = None) -> str | None:
    return language or os.getenv("PROJECT_BRAIN_TRANSCRIPTION_LANGUAGE") or None


def get_whisper_quality_config(language: str | None = None) -> WhisperQualityConfig:
    return WhisperQualityConfig(language=get_default_language(language))


def build_whisper_transcribe_kwargs(language: str | None = None, initial_prompt: str | None = None, retry: bool = False) -> dict:
    config = get_whisper_quality_config(language)
    kwargs = {
        "fp16": config.fp16,
        "temperature": config.temperature,
        "condition_on_previous_text": config.condition_on_previous_text,
        "compression_ratio_threshold": config.compression_ratio_threshold,
        "logprob_threshold": config.logprob_threshold,
        "no_speech_threshold": config.no_speech_threshold,
    }

    if config.language:
        kwargs["language"] = config.language

    if retry:
        kwargs.update({"beam_size": 5, "best_of": 5, "temperature": 0.0})
    else:
        kwargs.update({"beam_size": config.beam_size, "best_of": config.best_of})

    if initial_prompt:
        kwargs["initial_prompt"] = initial_prompt[:1200]

    return kwargs
