import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple

from PIL import Image


def extract_video_frames(
    video_path: str,
    interval_seconds: int = 30,
    max_frames: int = 30,
) -> List[str]:
    """
    Extract representative frames from video using ffmpeg.

    interval_seconds=30 means roughly one frame every 30 seconds.
    max_frames limits cost and processing time.
    """
    output_dir = tempfile.mkdtemp(prefix="project_brain_screen_frames_")
    output_pattern = str(Path(output_dir) / "frame_%04d.jpg")

    fps_value = f"1/{max(interval_seconds, 1)}"

    command = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vf",
        f"fps={fps_value}",
        "-frames:v",
        str(max_frames),
        "-q:v",
        "3",
        output_pattern,
    ]

    subprocess.run(
        command,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return sorted(str(p) for p in Path(output_dir).glob("frame_*.jpg"))


def _average_hash(image_path: str, hash_size: int = 8) -> str:
    """
    Simple perceptual hash. Good enough to remove nearly identical screens.
    """
    with Image.open(image_path) as image:
        image = image.convert("L").resize((hash_size, hash_size))
        pixels = list(image.getdata())
        avg = sum(pixels) / len(pixels)
        bits = ["1" if pixel > avg else "0" for pixel in pixels]
        return "".join(bits)


def _hamming_distance(a: str, b: str) -> int:
    return sum(ch1 != ch2 for ch1, ch2 in zip(a, b))


def deduplicate_similar_frames(
    frame_paths: List[str],
    max_distance: int = 6,
) -> Tuple[List[str], dict]:
    """
    Remove near-duplicate frames using average hash.

    Lower max_distance = stricter deduplication.
    Higher max_distance = more aggressive deduplication.
    """
    unique_frames = []
    unique_hashes = []
    skipped = 0

    for path in frame_paths:
        try:
            frame_hash = _average_hash(path)
        except Exception:
            unique_frames.append(path)
            continue

        is_duplicate = any(
            _hamming_distance(frame_hash, existing_hash) <= max_distance
            for existing_hash in unique_hashes
        )

        if is_duplicate:
            skipped += 1
            continue

        unique_frames.append(path)
        unique_hashes.append(frame_hash)

    return unique_frames, {
        "input_frames": len(frame_paths),
        "unique_frames": len(unique_frames),
        "skipped_duplicates": skipped,
        "hash_distance": max_distance,
    }


def cleanup_frames(frame_paths: List[str]):
    if not frame_paths:
        return

    frame_dir = Path(frame_paths[0]).parent

    try:
        shutil.rmtree(frame_dir, ignore_errors=True)
    except Exception:
        pass

