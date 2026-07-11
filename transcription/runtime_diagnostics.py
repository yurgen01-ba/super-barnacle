from __future__ import annotations

import time
from typing import Any

import torch

from config import WHISPER_DEVICE, WHISPER_MODEL_NAME
from transcription.quality_config import get_whisper_quality_config


def format_duration(seconds: float) -> str:
    milliseconds = int(round(max(seconds, 0.0) * 1000))
    minutes, milliseconds = divmod(milliseconds, 60_000)
    whole_seconds, milliseconds = divmod(milliseconds, 1_000)
    return f"{minutes:02d}:{whole_seconds:02d}.{milliseconds:03d}"


def get_whisper_runtime_diagnostics(model: Any | None = None) -> dict:
    config = get_whisper_quality_config()
    cuda_available = bool(torch.cuda.is_available())

    gpu_name = None
    gpu_memory_total_mb = None
    gpu_memory_allocated_mb = None

    if cuda_available:
        try:
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory_total_mb = round(
                torch.cuda.get_device_properties(0).total_memory / 1024 / 1024,
                1,
            )
            gpu_memory_allocated_mb = round(
                torch.cuda.memory_allocated(0) / 1024 / 1024,
                1,
            )
        except Exception:
            pass

    actual_device = str(getattr(model, "device", "not_loaded")) if model is not None else "not_loaded"
    requested_device = str(WHISPER_DEVICE or "auto")
    fp16_requested = bool(config.fp16)
    fp16_effective = bool(
        fp16_requested
        and cuda_available
        and "cuda" in actual_device.lower()
    )

    warning = None
    if requested_device.lower().startswith("cuda") and not cuda_available:
        warning = (
            "CUDA was requested, but torch.cuda.is_available() is False. "
            "The installed PyTorch build is likely CPU-only."
        )
    elif requested_device.lower().startswith("cuda") and "cuda" not in actual_device.lower():
        warning = (
            f"CUDA was requested, but Whisper is loaded on '{actual_device}'."
        )

    return {
        "whisper_model": WHISPER_MODEL_NAME,
        "requested_device": requested_device,
        "actual_device": actual_device,
        "cuda_available": cuda_available,
        "torch_version": torch.__version__,
        "torch_cuda_runtime": torch.version.cuda,
        "gpu_name": gpu_name,
        "gpu_memory_total_mb": gpu_memory_total_mb,
        "gpu_memory_allocated_mb": gpu_memory_allocated_mb,
        "fp16_requested": fp16_requested,
        "fp16_effective": fp16_effective,
        "beam_size": config.beam_size,
        "best_of": config.best_of,
        "temperature": config.temperature,
        "condition_on_previous_text": config.condition_on_previous_text,
        "warning": warning,
    }


def build_segment_performance_record(
    segment_index: int,
    total_segments: int,
    started_at: float,
    retried: bool,
    text_length: int,
    quality: dict | None = None,
) -> dict:
    elapsed_seconds = round(time.time() - started_at, 3)
    return {
        "segment_index": segment_index,
        "total_segments": total_segments,
        "inference_seconds": elapsed_seconds,
        "inference_time": format_duration(elapsed_seconds),
        "retried": bool(retried),
        "text_length": int(text_length),
        "quality": quality or {},
    }
