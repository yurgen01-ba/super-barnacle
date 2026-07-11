# Commit 20 — Vision First + Ollama Health Check

## Problem

User selected qwen2.5vl:7b, but it still looked like nothing happened.

Root cause:
The pipeline ran audio transcription and transcript extraction before screen analysis.
So Ollama did not start immediately.

## Added

```text
providers/vision/health.py
```

## Replaced

```text
extractors/meeting.py
ui/meetings.py
```

## Changed

- Screen analysis now runs before audio transcription.
- UI shows live Ollama progress immediately.
- Added "Test Ollama connection" button.
- Default max frames changed to 1 for first safe test.
- Default timeout changed to 180s.
- Default selected model is qwen2.5vl:7b because it is installed on your machine.

## Apply

Copy files into your project:

```text
providers/vision/health.py
extractors/meeting.py
ui/meetings.py
```

Run:

```powershell
python -m streamlit run app.py
```

Recommended test:
- Enable screen analysis.
- Click "Test Ollama connection".
- Max frames = 1.
- Model = qwen2.5vl:7b.
- Timeout = 180s.
- Process a short video.

Commit:

```powershell
git add .
git commit -m "Commit 20 - Run vision first and add Ollama health check"
```
