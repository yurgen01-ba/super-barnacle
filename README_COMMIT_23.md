# Commit 23 — Local Transcript Knowledge Extraction via Ollama

## Goal

Replace paid Claude extraction in the meeting transcript pipeline with local/free Ollama text extraction.

## Added

```text
providers/text/base.py
providers/text/ollama_provider.py
providers/text/factory.py
providers/text/health.py
ai/local_meeting_extractor.py
```

## Replaced

```text
extractors/meeting.py
ui/meetings.py
```

## New behavior

Meetings tab now has Transcript knowledge extraction options:

- `ollama` — local/free, default
- `claude` — paid fallback

Default local text model:

```text
qwen2.5:7b
```

Recommended setup:

```powershell
ollama pull qwen2.5:7b
```

For weaker machines:

```powershell
ollama pull qwen2.5:3b
```

## Apply

Copy files into your project:

```text
providers/text/
ai/local_meeting_extractor.py
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
git commit -m "Commit 23 - Add local transcript extractor via Ollama"
```
