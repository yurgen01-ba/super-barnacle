# Commit 6 — Jira Ticket Drafts

## Added files

Copy these files into your project:

```text
ai/jira_ticket_generator.py
ui/jira_ticket_drafts.py
```

## Update app.py

Add this import near other UI imports:

```python
from ui.jira_ticket_drafts import render_jira_ticket_drafts_tab
```

Find the tabs list:

```python
tab_video, tab_slack, tab_jira, tab_memory, tab_report = st.tabs([
    "🎥 Meetings",
    "💬 Slack",
    "📋 Jira",
    "🧠 Memory",
    "📊 Report",
])
```

Replace it with:

```python
tab_video, tab_slack, tab_jira, tab_memory, tab_report, tab_jira_drafts = st.tabs([
    "🎥 Meetings",
    "💬 Slack",
    "📋 Jira",
    "🧠 Memory",
    "📊 Report",
    "🧾 Jira Drafts",
])
```

Then after the Report tab block:

```python
with tab_report:
    render_report_tab(memory_repository)
```

Add:

```python
with tab_jira_drafts:
    render_jira_ticket_drafts_tab(memory_repository)
```

## What this adds

New tab:

```text
🧾 Jira Drafts
```

It generates Jira-ready tickets from Project Memory.

Each ticket contains:
- issue_type
- summary
- description
- acceptance_criteria
- priority
- labels
- source_basis
- notes_for_ba

## Run

```powershell
python -m streamlit run app.py
```

If works:

```powershell
git add .
git commit -m "Commit 6 - Add Jira ticket draft generator"
```
