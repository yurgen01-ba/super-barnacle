# Commit 189.6 — Block Bad Transcript Segments from Knowledge Extraction

```powershell
git add extractors/meeting.py README_COMMIT_189_6_BLOCK_BAD_TRANSCRIPT_SEGMENTS.md
git commit -m "Commit 189.6 - Block Bad Transcript Segments from Knowledge Extraction"
```

## Validate

```powershell
python -m py_compile extractors/meeting.py
python -m streamlit run app.py
```
