# Commit 38.2 — Improve Meeting Knowledge Extraction Recall

## Goal

Increase the amount and quality of extracted project knowledge from long meeting transcripts without changing the architecture.

This patch targets the issue where a long informative meeting produced too few knowledge items/facts.

## Added

```text
ai/json_repair.py
```

A shared lightweight JSON repair utility for local LLM responses.

It handles common Ollama/Qwen output issues:

```text
- markdown fences
- text before/after JSON
- trailing commas
- Python None/True/False
- missing commas between objects
```

## Replaced

```text
ai/local_meeting_extractor.py
ai/fact_extractor.py
utils/text.py
extractors/meeting.py
```

## What changed

### 1. Smaller overlapping chunks

Before:

```python
chunk_text(transcript, max_chars=10000)
```

After:

```python
chunk_text(transcript, max_chars=8000, overlap_chars=800)
```

This improves recall around chunk boundaries and makes local LLM prompts less overloaded.

### 2. Denser knowledge extraction

The meeting extractor now asks for more granular items:

```text
20–60 knowledge items per informative chunk
```

Instead of broad summaries.

### 3. Denser canonical fact extraction

Fact extraction target increased to:

```text
30–80 facts per informative chunk
```

It explicitly extracts:

```text
fields
statuses
rules
exceptions
actor responsibilities
API details
data dependencies
```

### 4. More robust JSON loading

Both extractors now use:

```python
safe_json_array_loads()
```

So slightly malformed local model output is less likely to produce empty extraction.

## Expected effect

For a 1.5 hour informative meeting, extracted items should increase significantly.

Expected direction:

```text
fewer empty chunks
more facts
more knowledge items
better Domain/Actors/Processes later
```

## Apply

Copy:

```text
ai/json_repair.py
ai/local_meeting_extractor.py
ai/fact_extractor.py
utils/text.py
extractors/meeting.py
```

Then run:

```powershell
python -m streamlit run app.py
```

Process a meeting and compare:

```text
canonical_facts_count
transcript_items_count
chunks_count
```

Commit:

```powershell
git add ai/json_repair.py ai/local_meeting_extractor.py ai/fact_extractor.py utils/text.py extractors/meeting.py README_COMMIT_38_2.md
git commit -m "Commit 38.2 - Improve meeting knowledge extraction recall"
```
