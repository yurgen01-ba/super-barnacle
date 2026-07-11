# Commit 9 — Store Documents and Chunks

## Problem

Project Memory only stored extracted knowledge items. If extractor returned `[]`, it looked like the uploaded source did not affect the system at all.

## Added

```text
repositories/source_repository.py
```

## Replaced

```text
memory/db.py
ui/meetings.py
ui/slack.py
ui/jira.py
ui/memory.py
```

## New tables

```text
documents
chunks
```

## New behavior

After processing:
- Meeting video transcript is saved as a source document.
- Slack paste is saved as a source document.
- Jira pasted text is saved as a source document.
- Jira PDF extracted text is saved as a source document.
- Each document is split into chunks and stored.
- Memory tab now shows:
  - Knowledge items
  - Timeline events
  - Source documents
  - Chunk preview

## Why this matters

Even if Claude extracts zero knowledge items, Project Brain still stores the source material and chunks. This prepares the product for:
- re-processing with new prompts;
- search;
- RAG;
- traceability;
- Knowledge Graph.

## Apply

Copy files into your project:

```text
memory/db.py
repositories/source_repository.py
ui/meetings.py
ui/slack.py
ui/jira.py
ui/memory.py
```

Run:

```powershell
python -m streamlit run app.py
```

Commit:

```powershell
git add .
git commit -m "Commit 9 - Store source documents and chunks"
```
