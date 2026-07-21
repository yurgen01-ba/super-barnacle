from __future__ import annotations

import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from transcription.audio_contracts import AudioTranscriptionResult, TranscriptSegment
from transcription.quality_score import score_transcript_segment


@dataclass(slots=True)
class RepairWindow:
    start_index: int
    end_index: int
    start: float
    end: float
    reasons: list[str]


def _word_confidence(segment: TranscriptSegment) -> float | None:
    scores = [word.score for word in segment.words if word.score is not None]
    if not scores:
        return segment.confidence
    return sum(scores) / len(scores)


def _is_suspicious(segment: TranscriptSegment, language: str) -> tuple[bool, list[str]]:
    quality = score_transcript_segment(segment.text, language)
    meaningful_reasons = [reason for reason in quality.reasons if reason != "too_few_words"]
    confidence = _word_confidence(segment)
    if confidence is not None and confidence < 0.42:
        meaningful_reasons.append(f"low_word_confidence:{confidence:.3f}")
    return bool(meaningful_reasons and quality.score < 0.68), meaningful_reasons


def find_repair_windows(
    segments: list[TranscriptSegment],
    language: str = "ru",
    min_bad_seconds: float = 6.0,
    max_gap_seconds: float = 1.25,
) -> list[RepairWindow]:
    flagged: list[tuple[int, list[str]]] = []
    for index, segment in enumerate(segments):
        suspicious, reasons = _is_suspicious(segment, language)
        if suspicious:
            flagged.append((index, reasons))
    if not flagged:
        return []

    windows: list[RepairWindow] = []
    group: list[tuple[int, list[str]]] = [flagged[0]]
    for item in flagged[1:]:
        previous_index = group[-1][0]
        if segments[item[0]].start - segments[previous_index].end <= max_gap_seconds:
            group.append(item)
        else:
            _append_window(windows, group, segments, min_bad_seconds)
            group = [item]
    _append_window(windows, group, segments, min_bad_seconds)
    return windows


def _append_window(
    windows: list[RepairWindow],
    group: list[tuple[int, list[str]]],
    segments: list[TranscriptSegment],
    min_bad_seconds: float,
) -> None:
    start_index = group[0][0]
    end_index = group[-1][0]
    start = segments[start_index].start
    end = segments[end_index].end
    if end - start < min_bad_seconds:
        return
    windows.append(
        RepairWindow(
            start_index=start_index,
            end_index=end_index,
            start=start,
            end=end,
            reasons=sorted({reason for _, reasons in group for reason in reasons}),
        )
    )


def _extract_clip(source: str, target: str, start: float, end: float) -> None:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg is required for local transcript repair")
    subprocess.run(
        [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", source,
            "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", target,
        ],
        check=True,
        capture_output=True,
    )


def _speaker_for_segment(
    segment: TranscriptSegment,
    originals: list[TranscriptSegment],
    offset: float,
) -> str | None:
    absolute_start = segment.start + offset
    absolute_end = segment.end + offset
    best_speaker = None
    best_overlap = 0.0
    for original in originals:
        overlap = max(0.0, min(absolute_end, original.end) - max(absolute_start, original.start))
        if overlap > best_overlap:
            best_overlap = overlap
            best_speaker = original.speaker
    return best_speaker or next((item.speaker for item in originals if item.speaker), None)


def _shift_segments(
    retry_segments: list[TranscriptSegment],
    originals: list[TranscriptSegment],
    offset: float,
) -> list[TranscriptSegment]:
    shifted: list[TranscriptSegment] = []
    for segment in retry_segments:
        speaker = _speaker_for_segment(segment, originals, offset)
        segment.start += offset
        segment.end += offset
        segment.speaker = speaker
        for word in segment.words:
            if word.start is not None:
                word.start += offset
            if word.end is not None:
                word.end += offset
            word.speaker = speaker
        shifted.append(segment)
    return shifted


def repair_transcript_segments(
    audio_path: str,
    segments: list[TranscriptSegment],
    retranscribe: Callable[[str], AudioTranscriptionResult],
    language: str = "ru",
    min_bad_seconds: float = 6.0,
    min_quality_gain: float = 0.12,
    clip_extractor: Callable[[str, str, float, float], None] = _extract_clip,
) -> tuple[list[TranscriptSegment], list[dict]]:
    windows = find_repair_windows(segments, language, min_bad_seconds)
    if not windows:
        return segments, []

    repaired = list(segments)
    debug: list[dict] = []
    index_shift = 0
    with tempfile.TemporaryDirectory(prefix="project_brain_repair_") as temp_dir:
        for window_number, window in enumerate(windows):
            originals = segments[window.start_index:window.end_index + 1]
            before_text = " ".join(item.text.strip() for item in originals if item.text.strip())
            before_quality = score_transcript_segment(before_text, language)
            clip_path = str(Path(temp_dir) / f"repair_{window_number:03d}.wav")
            event = {
                "start": window.start,
                "end": window.end,
                "duration": round(window.end - window.start, 3),
                "reasons": window.reasons,
                "before_score": before_quality.score,
                "accepted": False,
            }
            try:
                clip_extractor(audio_path, clip_path, window.start, window.end)
                retry = retranscribe(clip_path)
                after_text = " ".join(
                    item.text.strip() for item in retry.segments if item.text.strip()
                )
                after_quality = score_transcript_segment(after_text, language)
                event["after_score"] = after_quality.score
                event["quality_gain"] = round(after_quality.score - before_quality.score, 3)
                length_ratio = len(after_text) / max(len(before_text), 1)
                event["length_ratio"] = round(length_ratio, 3)
                if (
                    retry.segments
                    and after_quality.score >= before_quality.score + min_quality_gain
                    and 0.45 <= length_ratio <= 2.5
                ):
                    replacement = _shift_segments(retry.segments, originals, window.start)
                    start_index = window.start_index + index_shift
                    end_index = window.end_index + index_shift + 1
                    repaired[start_index:end_index] = replacement
                    index_shift += len(replacement) - len(originals)
                    event["accepted"] = True
            except Exception as exc:
                event["error"] = str(exc)
            debug.append(event)

    for index, segment in enumerate(repaired):
        segment.id = index
    return repaired, debug
