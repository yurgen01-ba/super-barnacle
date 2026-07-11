# Commit 16 — AI Vision Provider Layer

## Goal

Introduce a provider abstraction for visual analysis so Project Brain is not hardcoded to Ollama/Qwen.

## Added

```text
providers/vision/base.py
providers/vision/ollama_provider.py
providers/vision/factory.py
```

## Replaced

```text
ai/ollama_vision.py
extractors/meeting.py
ui/meetings.py
```

## Current supported provider

```text
ollama
```

Uses local Qwen2.5-VL via Ollama.

## Planned future providers

- Gemini Flash Vision
- OpenAI vision model
- Claude Vision
- local OCR + text LLM

## Apply

Copy folders/files into your project:

```text
providers/
ai/ollama_vision.py
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
git commit -m "Commit 16 - Add AI vision provider layer"
```
