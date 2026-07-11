# Commit 189.2 — Rewrite meeting transcription serialization

Rewrites `transcribe_audio_segments()` so `TranscriptQuality` is serialized safely without `.dict()` / `.__dict__`.

## Fixes

- `TranscriptQuality` dataclass with `slots=True` has no `.__dict__`.
- Segment retry now updates transcript parts after choosing the better segment.
- Quality metadata is always a plain dictionary.
- The file passes Python syntax validation.

## Git commands

```powershell
git add extractors/meeting.py README_COMMIT_189_2_REWRITE_MEETING_TRANSCRIPTION.md
git commit -m "Commit 189.2 - Rewrite meeting transcription serialization"
```

## Validate

```powershell
python -m py_compile extractors/meeting.py
python -m streamlit run app.py
```
