# Commit 39 — UI v2 Shell Rewrite

## Goal

Stop patching the unstable UI v2 and rewrite only the UI shell.

Backend stays untouched.

## Main decision

No native Streamlit sidebar.

No sticky/min-height layout.

No HTML wrappers around Streamlit widgets.

UI is now a simple stable 3-column layout:

```text
menu_col | main_col | chat_col
```

## Added / replaced

```text
app.py
ui_v2/state.py
ui_v2/design.py
ui_v2/app_shell.py
ui_v2/layout/menu.py
ui_v2/layout/topbar.py
ui_v2/layout/chat.py
ui_v2/pages/dashboard.py
```

## Preserved

- Dashboard-first workflow.
- AI Assistant always available on the right.
- Artifacts tab inside AI Assistant.
- Upload from Dashboard.
- Advanced data loaders hidden under expander.
- Project Model hidden in Project menu → Модель проекта · Beta.
- Placeholder actions are disabled.

## Run

```powershell
python -m streamlit run app.py
```

## Switch to old UI

```powershell
$env:PROJECT_BRAIN_UI="old"
python -m streamlit run app.py
```

## Commit

```powershell
git add app.py ui_v2 README_COMMIT_39_UI_V2_SHELL_REWRITE.md
git commit -m "Commit 39 - Rewrite UI v2 shell"
```
