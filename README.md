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

# Atlassian Cloud connection

Project Brain can connect a normal Atlassian user account through OAuth 2.0 (3LO).
The application never receives or stores the user's Atlassian login or password.
It stores encrypted, revocable OAuth tokens separately for each Project Brain user
and project, then imports the Jira issues and Confluence content visible to that user.

Create an OAuth 2.0 integration in the Atlassian Developer Console and configure the
exact callback URL shown below. Add the Jira and Confluence read scopes listed in
`services/atlassian_oauth_service.py`.

```env
ATLASSIAN_CLIENT_ID=your-client-id
ATLASSIAN_CLIENT_SECRET=your-client-secret
ATLASSIAN_REDIRECT_URI=http://localhost:8501/?atlassian_callback=1
```

For production, use an HTTPS callback and set a stable
`PROJECT_BRAIN_TOKEN_ENCRYPTION_KEY`. The local development fallback key is generated
in the ignored `data/.oauth_token_key` file. After configuration, open project settings,
select **Atlassian**, authorize the account, then start synchronization for the required
site.
