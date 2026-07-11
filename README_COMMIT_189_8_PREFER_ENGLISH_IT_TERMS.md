# Commit 189.8 — Prefer English IT terms over invented Russian ASR words

This hotfix improves Whisper prompting for mixed Russian/English business and IT meetings.

## Changes

- tells Whisper that the meeting is Russian with frequent English IT and product terms;
- asks Whisper to preserve likely English terms instead of inventing Russian-like words;
- expands the prompt glossary with UI, API and product terminology;
- adds targeted repairs for recurring ASR mistakes.

## Git commands

```powershell
git add transcription/context_stitching.py transcription/domain_glossary.py README_COMMIT_189_8_PREFER_ENGLISH_IT_TERMS.md
git commit -m "Commit 189.8 - Prefer English IT terms in mixed-language transcription"
```

## Validate

```powershell
python -m py_compile transcription/context_stitching.py transcription/domain_glossary.py
$env:WHISPER_MODEL_NAME="large-v3"
python -m streamlit run app.py
```
