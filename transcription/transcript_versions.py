from __future__ import annotations


def build_transcript_versions(raw_transcript: str, clean_transcript: str, repaired_transcript: str) -> dict:
    return {
        "raw": raw_transcript or "",
        "clean": clean_transcript or raw_transcript or "",
        "repaired": repaired_transcript or clean_transcript or raw_transcript or "",
    }


def transcript_stats(versions: dict) -> dict:
    return {
        key: {
            "chars": len(value or ""),
            "words": len((value or "").split()),
        }
        for key, value in versions.items()
    }
