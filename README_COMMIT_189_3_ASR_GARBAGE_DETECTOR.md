# Commit 189.3 — Add ASR Garbage Detector

```powershell
git add transcription/asr_garbage_detector.py transcription/quality_score.py README_COMMIT_189_3_ASR_GARBAGE_DETECTOR.md
git commit -m "Commit 189.3 - Add ASR Garbage Detector"
```

## Validate

```powershell
python -m py_compile extractors/meeting.py
python -m streamlit run app.py
```
