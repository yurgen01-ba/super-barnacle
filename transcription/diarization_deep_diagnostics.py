from __future__ import annotations

import importlib.metadata
import os
import time
import traceback
from dataclasses import dataclass, field


def _package_version(package_name: str) -> str | None:
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None


@dataclass
class DiarizationDiagnostics:
    enabled: bool
    token_found: bool = False
    token_length: int = 0
    token_prefix: str | None = None
    whisperx_version: str | None = None
    pyannote_audio_version: str | None = None
    torch_version: str | None = None
    torch_cuda_runtime: str | None = None
    cuda_available: bool = False
    gpu_name: str | None = None
    device: str | None = None
    model_name: str | None = None
    stages: list[dict] = field(default_factory=list)
    diarization_turns: int = 0
    unique_turn_speakers: list[str] = field(default_factory=list)
    words_total: int = 0
    words_with_speaker: int = 0
    segments_total: int = 0
    segments_with_speaker: int = 0
    assigned_speaker_labels: list[str] = field(default_factory=list)
    completed: bool = False
    failure_type: str | None = None
    failure_message: str | None = None
    failure_traceback: str | None = None

    @classmethod
    def create(
        cls,
        enabled: bool,
        device: str,
        model_name: str | None = None,
    ) -> "DiarizationDiagnostics":
        import torch

        token = os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN")
        token_prefix = None
        if token:
            token_prefix = token[:5] + "…" if len(token) > 5 else "set"

        return cls(
            enabled=enabled,
            token_found=bool(token),
            token_length=len(token or ""),
            token_prefix=token_prefix,
            whisperx_version=_package_version("whisperx"),
            pyannote_audio_version=_package_version("pyannote.audio"),
            torch_version=str(torch.__version__),
            torch_cuda_runtime=str(torch.version.cuda),
            cuda_available=bool(torch.cuda.is_available()),
            gpu_name=(
                torch.cuda.get_device_name(0)
                if torch.cuda.is_available()
                else None
            ),
            device=device,
            model_name=model_name,
        )

    def start_stage(self, name: str, details: dict | None = None) -> float:
        started_at = time.perf_counter()
        self.stages.append(
            {
                "name": name,
                "status": "started",
                "started_at_monotonic": started_at,
                "details": details or {},
            }
        )
        return started_at

    def complete_stage(
        self,
        name: str,
        started_at: float,
        details: dict | None = None,
    ) -> None:
        elapsed = round(time.perf_counter() - started_at, 3)
        self.stages.append(
            {
                "name": name,
                "status": "completed",
                "elapsed_seconds": elapsed,
                "details": details or {},
            }
        )

    def fail_stage(
        self,
        name: str,
        started_at: float,
        exc: Exception,
    ) -> None:
        elapsed = round(time.perf_counter() - started_at, 3)
        self.failure_type = type(exc).__name__
        self.failure_message = str(exc)
        self.failure_traceback = traceback.format_exc()
        self.stages.append(
            {
                "name": name,
                "status": "failed",
                "elapsed_seconds": elapsed,
                "error_type": self.failure_type,
                "error_message": self.failure_message,
            }
        )

    def inspect_diarization_turns(self, turns) -> None:
        speakers: set[str] = set()
        count = 0

        try:
            for _, _, speaker in turns.itertracks(yield_label=True):
                count += 1
                speakers.add(str(speaker))
        except Exception:
            try:
                count = len(turns)
                if hasattr(turns, "speaker"):
                    speakers.update(
                        str(value)
                        for value in turns["speaker"].dropna().unique()
                    )
            except Exception:
                pass

        self.diarization_turns = count
        self.unique_turn_speakers = sorted(speakers)

    def inspect_assignment(self, result: dict) -> None:
        segments = result.get("segments") or []
        self.segments_total = len(segments)

        words_total = 0
        words_with_speaker = 0
        segments_with_speaker = 0
        labels: set[str] = set()

        for segment in segments:
            segment_speaker = segment.get("speaker")
            if segment_speaker:
                segments_with_speaker += 1
                labels.add(str(segment_speaker))

            for word in segment.get("words") or []:
                words_total += 1
                speaker = word.get("speaker")
                if speaker:
                    words_with_speaker += 1
                    labels.add(str(speaker))

        self.words_total = words_total
        self.words_with_speaker = words_with_speaker
        self.segments_with_speaker = segments_with_speaker
        self.assigned_speaker_labels = sorted(labels)
        self.completed = bool(labels)

    def to_dict(self) -> dict:
        payload = dict(self.__dict__)
        for stage in payload.get("stages", []):
            stage.pop("started_at_monotonic", None)
        return payload
