# Transcription Segment Callback Contract

## Goal

Meeting transcription must emit an event after every completed audio segment.

This enables the flow:

```text
audio segment transcribed
↓
segment saved to DB
↓
canonical fact created
↓
project graph updated
↓
next segment starts
```

## Required event

The meeting extractor should call `audio_progress_callback` after each segment:

```python
audio_progress_callback({
    "event": "audio_segment_completed",
    "current": current_segment_no,
    "total": total_segments,
    "text": segment_transcript,
    "segment_path": str(segment_path),
})
```

## Existing progress event

Before segment transcription:

```python
audio_progress_callback({
    "event": "audio_segment_started",
    "current": current_segment_no,
    "total": total_segments,
    "segment_path": str(segment_path),
})
```

## Implementation note

If `extractors/meeting.py` currently emits `audio_segment_completed` without `text`,
update it to include the segment transcript text.

The persistence layer in `jobs/segment_persistence.py` expects one of:

```text
text
transcript
segment_text
```

## Why this matters

Without this event payload, the UI can show progress, but Project Brain cannot persist partial transcript data until the entire video is finished.
