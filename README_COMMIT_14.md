# Commit 14 — Visual Intelligence for Meeting Videos

## Problem

Meeting videos were analyzed only through audio transcription.
Screen content was ignored.

## Added

```text
ai/screen_extractor.py
extractors/screen.py
```

## Replaced

```text
extractors/meeting.py
ui/meetings.py
```

## New behavior

Meetings tab now has optional checkbox:

```text
Analyze screen content from video
```

When enabled:
- ffmpeg extracts representative frames from the video;
- Claude Vision analyzes visible screen content;
- extracted screen knowledge is merged with transcript knowledge;
- screen analysis is saved as source document;
- screen items are saved to Project Memory.

## What it can extract

- Jira issue information
- Confluence page content
- UI fields/buttons/flows
- diagrams
- API/Swagger information
- terminal errors
- code/IDE observations
- tables/forms/statuses

## Cost control

Screen analysis is disabled by default.

User can configure:
- frame interval in seconds;
- max number of frames.

## Apply

Copy files into your project:

```text
ai/screen_extractor.py
extractors/screen.py
extractors/meeting.py
ui/meetings.py
```

Run:

```powershell
python -m streamlit run app.py
```

Commit:

```powershell
git add .
git commit -m "Commit 14 - Add visual intelligence for meeting videos"
```
