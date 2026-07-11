# Commit 21 — Save Screen Knowledge Immediately

## Problem

Ollama completed frame analysis:

```text
Completed frame 1/1: 1 items
```

but nothing appeared in the database immediately.

Root cause:
screen items were returned only after the entire `process_meeting_video()` finished,
including audio transcription and transcript extraction.

## Replaced

```text
extractors/meeting.py
ui/meetings.py
```

## Changed

- Added `screen_items_callback` to `process_meeting_video`.
- Screen items are saved to Project Memory immediately after visual analysis.
- Screen analysis is also saved as a source document immediately.
- Final save step saves only transcript items to avoid duplicate screen records.
- Debug now includes `screen_items_saved_early`.

## Apply

Copy files into your project:

```text
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
git commit -m "Commit 21 - Save screen knowledge immediately"
```
