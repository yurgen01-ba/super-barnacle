from __future__ import annotations


def should_retry_segment(quality: dict, min_score: float = 0.55) -> bool:
    if not quality:
        return False
    return float(quality.get("score") or 0) < min_score


def choose_better_segment(first: dict, retry: dict) -> dict:
    first_score = float((first.get("quality") or {}).get("score") or 0)
    retry_score = float((retry.get("quality") or {}).get("score") or 0)
    return retry if retry_score > first_score else first
