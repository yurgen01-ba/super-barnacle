# Commit 19 — Live Vision Progress

## Problem

Even with safe local vision mode, Ollama can feel stuck because results only appear after the whole screen analysis finishes.

## Replaced

```text
providers/vision/base.py
providers/vision/ollama_provider.py
extractors/meeting.py
ui/meetings.py
```

## Changed

- Vision provider now supports `progress_callback`.
- Ollama analysis emits events:
  - frames ready
  - frame started
  - frame completed
  - frame failed
- Meeting UI now shows live screen analysis log.
- Progress updates after every frame.
- If a frame fails, the next frame continues.

## Apply

Copy files into your project:

```text
providers/vision/base.py
providers/vision/ollama_provider.py
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
git commit -m "Commit 19 - Add live vision progress"
```
