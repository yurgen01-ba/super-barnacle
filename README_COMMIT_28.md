# Commit 28 — Integrate Canonical Facts into Meeting Pipeline

## Goal

Connect the Canonical Facts foundation from Commit 27 to actual meeting video processing.

## Replaced

```text
builders/fact_builder.py
extractors/meeting.py
ui/meetings.py
```

## What changed

The meeting pipeline now does:

```text
Video
  ↓
Screen analysis optional
  ↓
Whisper transcript
  ↓
Transcript chunks
  ↓
Canonical Fact extraction
  ↓
Fact Store
  ↓
Knowledge Item extraction
  ↓
Project Memory
```

## UI changes

Meetings tab now has a new section:

```text
Canonical Facts
```

Controls:
- enable/disable fact extraction;
- fact extractor model;
- timeout per chunk;
- Ollama host;
- model health check.

Live progress:
- fact extraction started;
- chunk N/M started;
- chunk N/M completed;
- facts count;
- saved/skipped count.

## Important

This does not break existing knowledge extraction.
Facts are saved to the new `facts` table.
Knowledge items still work as before.

## Requirements

You need Commit 27 files installed first:

```text
core/fact_types.py
memory/fact_schema.py
repositories/fact_repository.py
ai/fact_extractor.py
```

Recommended model:

```powershell
ollama pull qwen2.5:7b
```

Lighter:

```powershell
ollama pull qwen2.5:3b
```

## Apply

Copy:

```text
builders/fact_builder.py
extractors/meeting.py
ui/meetings.py
```

Run:

```powershell
python -m streamlit run app.py
```

Commit:

```powershell
git add .
git commit -m "Commit 28 - Integrate canonical facts into meeting pipeline"
```
