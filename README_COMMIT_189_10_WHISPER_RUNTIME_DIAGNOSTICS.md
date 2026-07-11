# Commit 189.10 — Add Whisper Runtime Diagnostics

Adds automatic runtime and per-segment performance diagnostics.

## Captured data

- Whisper model;
- requested and actual device;
- CUDA availability;
- GPU model and memory;
- FP16 requested/effective;
- beam size, best-of and temperature;
- PyTorch and CUDA runtime versions;
- inference duration for every segment;
- whether a segment was retried.

## UI

The data is shown in:

- Transcription Diagnostics;
- reusable Developer Debug component;
- generated `transcription_runtime` artifact.

## Git commands

```powershell
git add transcription/runtime_diagnostics.py extractors/meeting.py jobs/extraction_artifact_integration.py ui_v2/pages/transcription_diagnostics.py ui_v2/components/whisper_runtime_debug.py README_COMMIT_189_10_WHISPER_RUNTIME_DIAGNOSTICS.md
git commit -m "Commit 189.10 - Add Whisper runtime diagnostics"
```

## Validate

```powershell
python -m py_compile transcription/runtime_diagnostics.py extractors/meeting.py jobs/extraction_artifact_integration.py ui_v2/pages/transcription_diagnostics.py ui_v2/components/whisper_runtime_debug.py
python -m streamlit run app.py
```
