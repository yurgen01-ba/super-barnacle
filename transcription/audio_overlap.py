from __future__ import annotations
import subprocess, tempfile
from pathlib import Path

def split_video_to_overlapping_audio_segments(video_path: str, segment_seconds: int, overlap_seconds: int = 12) -> list[dict]:
    out = Path(tempfile.mkdtemp(prefix="project_brain_audio_overlap_"))
    probe = subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",video_path],
        check=True, capture_output=True, text=True
    )
    duration = float((probe.stdout or "0").strip() or 0)
    segment_seconds = max(1, int(segment_seconds))
    overlap_seconds = max(0, min(int(overlap_seconds), segment_seconds-1))
    step = segment_seconds-overlap_seconds
    result, start, idx = [], 0.0, 0
    while start < duration:
        end = min(start+segment_seconds, duration)
        path = out/f"segment_{idx:03d}.wav"
        subprocess.run(
            ["ffmpeg","-y","-ss",str(start),"-to",str(end),"-i",video_path,"-vn","-acodec","pcm_s16le","-ar","16000","-ac","1",str(path)],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        result.append({"path":str(path),"index":idx+1,"start_seconds":round(start,3),"end_seconds":round(end,3),"overlap_seconds":overlap_seconds})
        idx += 1
        start += step
    return result
