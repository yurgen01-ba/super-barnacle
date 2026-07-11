# Commit 87 — Design System Tokens

## Goal

Introduce a single design-system entry point and shared tokens.

## Added

```text
ui/design_tokens.py
ui/theme.py
```

## Commit

```powershell
git add ui/design_tokens.py ui/theme.py README_COMMIT_87_DESIGN_SYSTEM_TOKENS.md
git commit -m "Commit 87 - Add Project Brain design system tokens"
```

## Usage

Call once near app startup:

```python
from ui.theme import apply_project_brain_theme

apply_project_brain_theme()
```
