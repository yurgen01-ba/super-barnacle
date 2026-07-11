# Commit 38.6 — UI v2 Chat Panel and Button States

## Goal

Adjust UI v2 after visual review.

## Fixed

### 1. AI Chat as side panel

AI Assistant is now a permanent right-side panel again.

### 2. Button colors

CSS now forces Streamlit buttons to match the dark design:
- no white buttons;
- primary buttons use subtle blue;
- disabled buttons are visibly muted.

### 3. Non-functional elements are explicit

Placeholder buttons are now disabled:
- Add project;
- Project members;
- export/delete project;
- dashboard quick source cards;
- artifact generators.

Each placeholder has a small note explaining that it is not connected yet.

## Replace

```text
ui_v2/design.py
ui_v2/app_shell.py
ui_v2/layout/topbar.py
ui_v2/layout/assistant.py
ui_v2/layout/sidebar.py
ui_v2/pages/dashboard.py
```

## Run

```powershell
python -m streamlit run app.py
```

## Commit

```powershell
git add ui_v2/design.py ui_v2/app_shell.py ui_v2/layout/topbar.py ui_v2/layout/assistant.py ui_v2/layout/sidebar.py ui_v2/pages/dashboard.py README_COMMIT_38_6_UI_CHAT_PANEL.md
git commit -m "Commit 38.6 - Add UI v2 chat panel and button states"
```
