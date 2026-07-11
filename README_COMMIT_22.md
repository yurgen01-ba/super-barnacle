# Commit 22 — Live Audio Progress After Vision

## Problem

After visual analysis completed, it looked like nothing happened:

```text
Completed frame 8/8
```

Then the user expected transcription to start, but UI did not show audio progress.

## Replaced

```text
extractors/meeting.py
ui/meetings.py
```

## Changed

Added live audio/transcript progress events:

- video save started
- video ready
- audio stage started
- audio split started/completed
- Whisper started segment N/M
- Whisper completed segment N/M
- transcript ready
- Claude transcript extraction started
- Claude extraction chunk N/M completed/failed

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
git commit -m "Commit 22 - Add live audio progress after vision"
```
