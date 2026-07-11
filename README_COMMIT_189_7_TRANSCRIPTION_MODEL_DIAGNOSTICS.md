# Commit 189.7 — Add Transcription Model Diagnostics

```powershell
git add transcription/model_diagnostics.py ui_v2/pages/transcription_diagnostics.py README_COMMIT_189_7_TRANSCRIPTION_MODEL_DIAGNOSTICS.md
git commit -m "Commit 189.7 - Add Transcription Model Diagnostics"
```

## Validate

```powershell
python -m py_compile extractors/meeting.py
python -m streamlit run app.py
```
