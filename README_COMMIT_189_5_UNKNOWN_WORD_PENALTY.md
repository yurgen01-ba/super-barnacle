# Commit 189.5 — Lower Score for Unknown ASR Words

```powershell
git add transcription/unknown_word_detector.py transcription/quality_score.py README_COMMIT_189_5_UNKNOWN_WORD_PENALTY.md
git commit -m "Commit 189.5 - Lower Score for Unknown ASR Words"
```

## Validate

```powershell
python -m py_compile extractors/meeting.py
python -m streamlit run app.py
```
