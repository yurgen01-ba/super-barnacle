from __future__ import annotations

import os
import time
from collections import Counter

import torch
import whisperx
from whisperx.diarize import DiarizationPipeline

from config import (
    WHISPERX_BATCH_SIZE,
    WHISPERX_COMPUTE_TYPE,
    WHISPERX_DEVICE,
    WHISPERX_ENABLE_ALIGNMENT,
    WHISPERX_ENABLE_DIARIZATION,
    WHISPERX_HOTWORDS,
    WHISPERX_INITIAL_PROMPT,
    WHISPERX_LANGUAGE,
    WHISPERX_MODEL_NAME,
    WHISPERX_VAD_OFFSET,
    WHISPERX_VAD_ONSET,
)
from transcription.diarization_deep_diagnostics import DiarizationDiagnostics

from transcription.audio_contracts import (
    AudioTranscriptionResult,
    TranscriptSegment,
    WordTimestamp,
)


def _bool(value) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _dominant_speaker(words: list[dict]) -> str | None:
    speakers = [str(w.get("speaker")) for w in words if w.get("speaker")]
    return Counter(speakers).most_common(1)[0][0] if speakers else None


class WhisperXTranscriber:
    def __init__(self):
        self.device = str(WHISPERX_DEVICE)
        self.compute_type = str(WHISPERX_COMPUTE_TYPE)
        self.batch_size = int(WHISPERX_BATCH_SIZE)
        self.enable_alignment = _bool(WHISPERX_ENABLE_ALIGNMENT)
        self.enable_diarization = _bool(WHISPERX_ENABLE_DIARIZATION)
        self.language = str(WHISPERX_LANGUAGE) if WHISPERX_LANGUAGE else None
        self.model = whisperx.load_model(
            WHISPERX_MODEL_NAME,
            self.device,
            compute_type=self.compute_type,
            language=self.language,
            asr_options={
                "initial_prompt": (
                    str(WHISPERX_INITIAL_PROMPT or "") or None
                ) if self.language else None,
                "hotwords": str(WHISPERX_HOTWORDS or "") or None,
                "condition_on_previous_text": True,
                "hallucination_silence_threshold": 1.5,
            },
            vad_options={
                "vad_onset": float(WHISPERX_VAD_ONSET),
                "vad_offset": float(WHISPERX_VAD_OFFSET),
            },
        )

    def transcribe(
        self,
        audio_path: str,
        language: str | None = None,
        min_speakers: int | None = None,
        max_speakers: int | None = None,
    ) -> AudioTranscriptionResult:
        started = time.time()
        warnings: list[str] = []
        diarization_debug = DiarizationDiagnostics.create(
            enabled=self.enable_diarization,
            device=self.device,
            model_name=str(WHISPERX_MODEL_NAME),
        )

        load_audio_started = diarization_debug.start_stage(
            "load_audio",
            {"audio_path": str(audio_path)},
        )
        try:
            audio = whisperx.load_audio(audio_path)
            diarization_debug.complete_stage(
                "load_audio",
                load_audio_started,
                {"audio_samples": len(audio)},
            )
        except Exception as exc:
            diarization_debug.fail_stage(
                "load_audio",
                load_audio_started,
                exc,
            )
            raise
        asr_started = diarization_debug.start_stage(
            "asr_transcription",
            {
                "language_mode": "explicit" if language else "auto",
                "requested_language": language,
                "batch_size": self.batch_size,
            },
        )
        effective_language = language or self.language
        raw = self.model.transcribe(
            audio,
            batch_size=self.batch_size,
            language=effective_language,
        )
        diarization_debug.complete_stage(
            "asr_transcription",
            asr_started,
            {
                "detected_language": raw.get("language"),
                "segments": len(raw.get("segments") or []),
            },
        )
        detected_language = str(raw.get("language") or effective_language or "unknown")
        result = raw
        alignment_used = False
        diarization_used = False

        if self.enable_alignment and detected_language != "unknown":
            alignment_started = diarization_debug.start_stage(
                "alignment",
                {"language": detected_language},
            )
            try:
                align_model, metadata = whisperx.load_align_model(
                    language_code=detected_language,
                    device=self.device,
                )
                result = whisperx.align(
                    raw.get("segments") or [],
                    align_model,
                    metadata,
                    audio,
                    self.device,
                    return_char_alignments=False,
                )
                result["language"] = detected_language
                alignment_used = True
                diarization_debug.complete_stage(
                    "alignment",
                    alignment_started,
                    {
                        "segments": len(result.get("segments") or []),
                    },
                )
                del align_model
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except Exception as exc:
                diarization_debug.fail_stage(
                    "alignment",
                    alignment_started,
                    exc,
                )
                warnings.append(
                    f"Alignment failed safely: {type(exc).__name__}: {exc}"
                )
                result = raw

        token = os.getenv("HUGGINGFACE_TOKEN") or os.getenv("HF_TOKEN")
        if self.enable_diarization:
            if not token:
                missing_token_started = diarization_debug.start_stage(
                    "validate_huggingface_token",
                )
                error = RuntimeError(
                    "HUGGINGFACE_TOKEN/HF_TOKEN is missing."
                )
                diarization_debug.fail_stage(
                    "validate_huggingface_token",
                    missing_token_started,
                    error,
                )
                warnings.append(
                    "Diarization enabled, but "
                    "HUGGINGFACE_TOKEN/HF_TOKEN is missing."
                )
            else:
                load_pipeline_started = diarization_debug.start_stage(
                    "load_diarization_pipeline",
                    {
                        "token_found": diarization_debug.token_found,
                        "token_length": diarization_debug.token_length,
                        "device": self.device,
                        "min_speakers": min_speakers,
                        "max_speakers": max_speakers,
                    },
                )
                try:
                    pipeline = DiarizationPipeline(
                        token=token,
                        device=self.device,
                    )
                    diarization_debug.complete_stage(
                        "load_diarization_pipeline",
                        load_pipeline_started,
                    )

                    run_diarization_started = diarization_debug.start_stage(
                        "run_diarization",
                    )
                    turns = pipeline(
                        audio,
                        min_speakers=min_speakers,
                        max_speakers=max_speakers,
                    )
                    diarization_debug.inspect_diarization_turns(turns)
                    diarization_debug.complete_stage(
                        "run_diarization",
                        run_diarization_started,
                        {
                            "turns": diarization_debug.diarization_turns,
                            "speakers": diarization_debug.unique_turn_speakers,
                        },
                    )

                    assign_started = diarization_debug.start_stage(
                        "assign_word_speakers",
                        {
                            "transcript_segments": len(
                                result.get("segments") or []
                            ),
                        },
                    )
                    result = whisperx.assign_word_speakers(
                        turns,
                        result,
                        fill_nearest=True,
                    )
                    diarization_debug.inspect_assignment(result)
                    diarization_debug.complete_stage(
                        "assign_word_speakers",
                        assign_started,
                        {
                            "words_total": diarization_debug.words_total,
                            "words_with_speaker": (
                                diarization_debug.words_with_speaker
                            ),
                            "segments_total": (
                                diarization_debug.segments_total
                            ),
                            "segments_with_speaker": (
                                diarization_debug.segments_with_speaker
                            ),
                            "speaker_labels": (
                                diarization_debug.assigned_speaker_labels
                            ),
                        },
                    )

                    diarization_used = diarization_debug.completed
                    if not diarization_used:
                        warnings.append(
                            "Diarization completed, but no speaker labels "
                            "were assigned. Inspect diarization_debug."
                        )

                    del pipeline
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()

                except Exception as exc:
                    current_stage = (
                        "run_or_assign_diarization"
                    )
                    diarization_debug.fail_stage(
                        current_stage,
                        load_pipeline_started,
                        exc,
                    )
                    warnings.append(
                        f"Diarization failed safely: "
                        f"{type(exc).__name__}: {exc}"
                    )

        segments = self._convert_segments(result.get("segments") or [])
        speaker_labels = sorted({segment.speaker for segment in segments if segment.speaker})
        text = " ".join(segment.text for segment in segments if segment.text).strip()

        return AudioTranscriptionResult(
            text=text,
            language=detected_language,
            segments=segments,
            backend="whisperx",
            model=str(WHISPERX_MODEL_NAME),
            runtime={
                "device": self.device,
                "compute_type": self.compute_type,
                "batch_size": self.batch_size,
                "cuda_available": bool(torch.cuda.is_available()),
                "gpu": (
                    torch.cuda.get_device_name(0)
                    if torch.cuda.is_available()
                    else None
                ),
                "seconds": round(time.time() - started, 3),
                "alignment": alignment_used,
                "diarization": diarization_used,
                "speaker_count": len(speaker_labels),
                "speaker_labels": speaker_labels,
                "diarization_debug": diarization_debug.to_dict(),
            },
            warnings=warnings,
        )

    def _convert_segments(self, items: list[dict]) -> list[TranscriptSegment]:
        segments: list[TranscriptSegment] = []

        for index, item in enumerate(items):
            raw_words = item.get("words") or []
            words = [
                WordTimestamp(
                    word=str(word.get("word") or "").strip(),
                    start=word.get("start"),
                    end=word.get("end"),
                    score=word.get("score"),
                    speaker=word.get("speaker"),
                )
                for word in raw_words
            ]

            segments.append(
                TranscriptSegment(
                    id=int(item.get("id", index)),
                    start=float(item.get("start") or 0),
                    end=float(item.get("end") or 0),
                    text=str(item.get("text") or "").strip(),
                    speaker=item.get("speaker") or _dominant_speaker(raw_words),
                    words=words,
                    confidence=item.get("score"),
                )
            )

        return segments
