# Project Brain v2.0

Clean, consistent version of Project Brain.

## Features

- Streamlit upload limit: 600 MB
- Meeting videos → ffmpeg audio segments → Whisper transcription → Claude extraction
- Slack paste → chunking → Claude extraction
- Jira text → chunking → Claude extraction
- Jira PDF export → text extraction → chunking → Claude extraction
- Robust JSON repair for Claude responses
- SQLite Project Memory
- Timeline
- Decision deduplication
- Report generation with visible spinner and diagnostics

## Install

```powershell
cd C:\Users\user\project-brain
python -m pip install -r requirements.txt
```

## .env

Create `.env` in project root:

```env
ANTHROPIC_API_KEY=your_key
WHISPER_MODEL_NAME=base
CLAUDE_EXTRACTOR_MODEL=claude-sonnet-4-6
CLAUDE_REPORT_MODEL=claude-sonnet-4-6
```

## FFmpeg

Check that ffmpeg works:

```powershell
ffmpeg -version
```

## Run

```powershell
python -m streamlit run app.py
```

## Important

If you replace an existing project, back it up first.
