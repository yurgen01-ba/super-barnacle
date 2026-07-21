from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path


SPEAKER_RE = re.compile(r"^SPEAKER_\d+$")


def _safe_part(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value or "unknown"))[:120]


def select_speaker_windows(result: dict, sample_seconds: float = 5.0) -> list[dict]:
    audio = result.get("audio_intelligence") or {}
    utterances = (
        audio.get("speaker_utterances")
        or result.get("speaker_utterances")
        or result.get("transcript_segments")
        or []
    )
    duration = float(result.get("duration_seconds") or 0.0)
    best: dict[str, dict] = {}
    for utterance in utterances:
        speaker = str(utterance.get("speaker") or "")
        if not SPEAKER_RE.match(speaker):
            continue
        start = float(utterance.get("start") or 0.0)
        end = float(utterance.get("end") or start)
        if end <= start:
            continue
        if speaker not in best or end - start > best[speaker]["utterance_duration"]:
            best[speaker] = {
                "speaker": speaker,
                "utterance_start": start,
                "utterance_end": end,
                "utterance_duration": end - start,
            }

    windows = []
    for speaker in sorted(best):
        item = best[speaker]
        center = (item["utterance_start"] + item["utterance_end"]) / 2
        start = max(0.0, center - sample_seconds / 2)
        if duration > 0:
            start = min(start, max(0.0, duration - sample_seconds))
            clip_duration = min(sample_seconds, duration - start)
        else:
            clip_duration = sample_seconds
        windows.append(
            {
                "speaker": speaker,
                "start": round(start, 3),
                "duration": round(max(0.1, clip_duration), 3),
            }
        )
    return windows


def create_speaker_samples(
    video_path: str,
    result: dict,
    *,
    project_id: str,
    job_id: str,
    file_name: str,
    output_root: str | Path = "data/speaker_samples",
) -> list[dict]:
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return []
    output_dir = Path(output_root) / _safe_part(project_id) / _safe_part(job_id)
    output_dir.mkdir(parents=True, exist_ok=True)
    samples = []
    for window in select_speaker_windows(result):
        target = output_dir / f"{_safe_part(file_name)}_{window['speaker']}.wav"
        try:
            subprocess.run(
                [
                    ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                    "-ss", f"{window['start']:.3f}", "-i", video_path,
                    "-t", f"{window['duration']:.3f}", "-vn", "-ac", "1",
                    "-ar", "16000", "-c:a", "pcm_s16le", str(target),
                ],
                check=True,
                capture_output=True,
            )
        except Exception:
            continue
        samples.append(
            {
                **window,
                "file_name": file_name,
                "clip_path": str(target.resolve()),
            }
        )
    return samples
