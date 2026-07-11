# Hotfix for Commit 38.6 — Chat Top and Dark Buttons

## Problem

- Right chat column showed an empty card, while actual chat content rendered below it.
- Some controls were still white, especially popover-like controls.
- Chat needed to start at the top of the right column.

## Fix

Replace:

```text
ui_v2/design.py
ui_v2/layout/assistant.py
ui_v2/layout/sidebar.py
```

## What changed

- Removed raw HTML wrapper around chat widgets.
- Chat content now renders from the top of the right column.
- Replaced sidebar `popover` with `expander` because popover remained white in current Streamlit theme.
- Strengthened button CSS selectors.

## Run

```powershell
python -m streamlit run app.py
```

## Commit

```powershell
git add ui_v2/design.py ui_v2/layout/assistant.py ui_v2/layout/sidebar.py README_HOTFIX_38_6_CHAT_TOP_BUTTONS.md
git commit -m "Hotfix UI v2 chat top and dark buttons"
```
