# Commit 40 — UI v2 Functionality Bindings

## Goal

Restore existing functionality inside the new UI v2 design.

No backend changes.

## Added / replaced

```text
ui_v2/state.py
ui_v2/layout/menu.py
ui_v2/layout/chat.py
ui_v2/pages/dashboard.py
ui_v2/pages/sources.py
ui_v2/app_shell.py
```

## What is now functional

### Dashboard source cards

Dashboard cards are now connected:

```text
Meetings → opens existing meeting processor
Slack → opens existing Slack importer
Confluence → opens existing Confluence importer
Jira → opens existing Jira importer
```

They open inside:

```text
Active data loader
```

### Sources menu

Left menu source items now open the Sources page and select the right source section:

```text
Meetings
Slack
Confluence
Jira
Files
```

### Sources page

The Sources page now renders existing source UIs by selected source.

### Chat artifacts tab

Artifacts tab now has entry-points:

```text
Confluence
Jira
Test cases
All artifacts
```

If an existing generator exists, it is rendered.
If not, the entry point is explicit but disabled/placeholder.

## Still intentionally not functional

```text
Add project
Project members
Export data
Delete project
Files importer
Jira artifact generator
Test case generator
```

These are visible placeholders.

## Run

```powershell
python -m streamlit run app.py
```

## Commit

```powershell
git add ui_v2 README_COMMIT_40_UI_V2_FUNCTIONALITY_BINDINGS.md
git commit -m "Commit 40 - Bind UI v2 to existing functionality"
```
