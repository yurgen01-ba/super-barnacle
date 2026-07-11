# Commit 17 — Automatic Audio Segment Size

## Problem

The user should not have to choose audio segment size manually.
This is a technical setting, not a product-level decision.

## Replaced

```text
extractors/meeting.py
ui/meetings.py
```

## Changed

- Removed segment size from the main UI.
- Added automatic segment selection based on video duration.
- Added optional override in "Advanced audio settings".
- Added debug info:
  - video duration
  - selected audio segment size
  - number of audio segments

## Automatic rules

```text
<= 15 min   → one segment
<= 60 min   → 15 min segments
<= 2 hours  → 20 min segments
> 2 hours   → 30 min segments
unknown     → 20 min segments
```

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
git commit -m "Commit 17 - Auto-select audio segment size"
```
