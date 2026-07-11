# Commit 27 — Canonical Facts Foundation

## Goal

Introduce the first layer of the Project Model Foundation: Canonical Facts.

This commit does **not** replace existing Project Memory.
It adds a new foundation layer next to current `knowledge`.

## New concept

A Canonical Fact is:

```text
subject → predicate → object
```

Examples:

```text
Merchant → can_have_status → Suspended
Funding → requires → KYC
Advance → approved_by → Underwriter
```

## Added files

```text
core/fact_types.py
memory/fact_schema.py
repositories/fact_repository.py
repositories/entity_repository.py
repositories/project_repository.py
builders/fact_builder.py
builders/entity_builder.py
ai/fact_extractor.py
ui/facts.py
```

## New DB tables

```text
facts
fact_evidence
entities
entity_facts
project_summary
```

These are created safely with `CREATE TABLE IF NOT EXISTS`.

## How to initialize schema

In `app.py`, add:

```python
from memory.fact_schema import init_fact_schema
```

Then after:

```python
init_db()
```

add:

```python
init_fact_schema()
```

## How to add Facts tab to Memory area

In `app.py`, add:

```python
from ui.facts import render_facts_tab
```

Then replace current memory rendering with tabs:

```python
tab_memory, tab_facts = st.tabs(["🧠 Knowledge", "🧩 Canonical Facts"])

with tab_memory:
    render_memory_tab(memory_repository)

with tab_facts:
    render_facts_tab()
```

## How to extract facts from a transcript later

Use:

```python
from builders.fact_builder import FactBuilder

builder = FactBuilder(
    model="qwen2.5:7b",
    host="http://localhost:11434",
)

result = builder.build_and_save_facts(
    text=transcript,
    source="meeting_video:example.mp4:transcript_chunk_1",
    source_type="meeting_transcript",
)
```

## Recommended next commit

Commit 28:
- integrate FactBuilder into meeting pipeline;
- save facts immediately after transcript chunk extraction;
- add live progress for fact extraction.
