# Commit 18 — Safe Local Vision Mode

## Problem

Ollama/Qwen visual analysis may not finish on weaker Windows machines.

## Replaced

```text
providers/vision/ollama_provider.py
providers/vision/factory.py
```

## Changed

- Default vision model changed to `qwen2.5vl:3b`.
- One frame is analyzed at a time.
- Timeout per frame added, default 60 seconds.
- If Ollama fails, screen analysis returns a safe warning item instead of crashing the whole pipeline.

## Recommended setup

```powershell
ollama pull qwen2.5vl:3b
```

## Apply

Copy files into your project:

```text
providers/vision/ollama_provider.py
providers/vision/factory.py
```

Run:

```powershell
python -m streamlit run app.py
```

Commit:

```powershell
git add .
git commit -m "Commit 18 - Add safe local vision mode"
```
