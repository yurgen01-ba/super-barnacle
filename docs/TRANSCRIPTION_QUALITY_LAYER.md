# Transcription Quality Layer

## Purpose

Improve meeting transcript quality before knowledge extraction.

## Pipeline

```text
Audio segment
 → Whisper high-quality decode
 → forced language
 → glossary repair
 → quality scoring
 → retry bad segment
 → context stitching
 → raw / clean / repaired transcript artifacts
 → facts / graph / project model
```

## Artifacts

- `transcript` — raw Whisper transcript
- `clean_transcript` — cleaned transcript
- `repaired_transcript` — glossary/repair-enhanced transcript used by downstream extraction
- `transcript_quality` — segment quality summary

## Diagnostics

Open:

```text
Transcription Quality
```

from the UI menu to compare transcript versions and inspect quality.
