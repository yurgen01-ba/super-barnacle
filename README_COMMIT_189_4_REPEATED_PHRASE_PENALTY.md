# Commit 189.4 — Penalize Repeated Phrases

```powershell
git add transcription/repetition_detector.py transcription/quality_score.py README_COMMIT_189_4_REPEATED_PHRASE_PENALTY.md
git commit -m "Commit 189.4 - Penalize Repeated Phrases"
```

## Validate

```powershell
python -m py_compile extractors/meeting.py
python -m streamlit run app.py
```
