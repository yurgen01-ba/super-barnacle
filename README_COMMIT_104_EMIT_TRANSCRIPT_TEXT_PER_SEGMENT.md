# Commit 104 — Emit Transcript Text per Segment

## Problem

`audio_segment_completed` events did not include the transcribed text.

As a result, `segment_persistence.py` received an empty segment, skipped saving it, and Project Graph stayed empty.

## Changed

```text
extractors/meeting.py
```

## Commit

```powershell
git add extractors/meeting.py README_COMMIT_104_EMIT_TRANSCRIPT_TEXT_PER_SEGMENT.md
git commit -m "Commit 104 - Emit transcript text after each audio segment"
```
