# UI Backlog

This file captures known UI issues and improvement ideas.

The UI is good enough to continue core development, but it still has weaknesses that should be addressed later.

## Current UI direction

```text
Left column: navigation and project controls
Center column: dashboard / workspace
Right column: AI Assistant
```

Important product decisions:

```text
AI Assistant is always available
Artifacts are generated from chat
Data ingestion is available from Dashboard
Project Model is hidden as advanced mode
Multi-project support is planned
```

## Known issues

### 1. Streamlit styling limitations

Some native Streamlit components are difficult to style consistently:

```text
expanders
popovers
buttons
tabs
file uploader
```

Decision: keep Streamlit for now, but avoid complex custom layouts with raw HTML wrappers.

### 2. Dashboard source cards are not final

Future improvement:

```text
status
last sync
items imported
errors
settings gear
primary action
```

### 3. AI Assistant needs better conversation state

Future improvement:

```text
message history
artifact generation
citations
mode selector
context selector
```

### 4. Project menu needs final design

Future improvement:

```text
project switcher
add project modal
project settings
members
advanced model access
export
```

### 5. Project Model is still too technical

Future improvement:

```text
graph view
entity profile
process profile
evidence explorer
confidence indicators
relationship map
```

### 6. Buttons and placeholders

Current placeholders:

```text
Add project
Project members
Export data
Delete project
Files importer
Jira artifact generator
Test case generator
```

## UI rule

Do not let UI refactoring block core intelligence development.

The next priority is Knowledge Graph Engine.
