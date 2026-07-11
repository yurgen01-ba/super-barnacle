from __future__ import annotations

from config import WHISPER_MODEL_NAME


LOW_QUALITY_MODELS = {"tiny", "base", "small"}


def get_transcription_model_diagnostics() -> dict:
    model = str(WHISPER_MODEL_NAME or "")
    model_key = model.lower().split(".")[0].split("-")[0]

    warning = None
    if model_key in LOW_QUALITY_MODELS:
        warning = (
            f"Current Whisper model '{WHISPER_MODEL_NAME}' may be too weak for noisy Russian project meetings. "
            "Use medium, large-v3, or turbo if available."
        )

    return {
        "model": WHISPER_MODEL_NAME,
        "is_low_quality_model": model_key in LOW_QUALITY_MODELS,
        "warning": warning,
        "recommended_models": ["medium", "large-v3", "turbo"],
    }
