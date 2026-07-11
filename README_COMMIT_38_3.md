# Commit 38.3 — Project Intelligence Refresh

## Goal

Stabilize the current manual builder workflow without introducing the full future Builder Registry yet.

This patch adds one compact Project Model tab:

```text
🚀 Refresh
```

It runs the current builders in the correct order:

```text
Entities
→ Relationships
→ Ontology
→ Domain Model
→ Actors
→ Processes
→ Project Summary
```

## Added

```text
ui/project_intelligence.py
```

## Updated

```text
ui/workspace/model.py
```

## Why this matters

Before this patch, the user had to remember the correct build order manually across multiple tabs.

After this patch, the user can open:

```text
Project Model → Refresh → Refresh Project Intelligence
```

and rebuild the model in one place.

This is not the final Pipeline Engine. It is a safe bridge that improves the current project immediately, while keeping the later BaseBuilder / Registry / Pipeline refactor possible.

## Apply

Copy:

```text
ui/project_intelligence.py
ui/workspace/model.py
README_COMMIT_38_3.md
```

Run:

```powershell
python -m streamlit run app.py
```

Then open:

```text
Project Model → 🚀 Refresh
```

Commit:

```powershell
git add ui/project_intelligence.py ui/workspace/model.py README_COMMIT_38_3.md
git commit -m "Commit 38.3 - Add Project Intelligence refresh workflow"
```
