# Commit 37 — Business Process Intelligence

## Goal

Add the first Process Intelligence layer to Project Brain.

Processes are not just facts or relationships. They are structured business workflows with:

- goal;
- participants;
- business objects;
- steps;
- inputs;
- outputs;
- rules;
- risks/exceptions/open questions;
- evidence.

## Added

```text
models/process.py
repositories/process_repository.py
builders/process_builder.py
ui/processes.py
```

## Updated

```text
memory/fact_schema.py
repositories/project_repository.py
repositories/chat_context_repository.py
builders/project_summary_builder.py
ai/project_chat.py
ui/workspace/model.py
```

## New DB table

```text
processes
```

Main columns:

```text
name
process_type
goal
participants_json
business_objects_json
steps_json
inputs_json
outputs_json
rules_json
exceptions_json
evidence_json
confidence
```

## New UI

Project Model now has:

```text
🗺️ Processes
```

It can:

- build/refresh Process Model;
- search processes;
- inspect participants;
- inspect business objects;
- inspect process steps;
- inspect inputs/outputs;
- inspect rules;
- inspect risks/exceptions/open questions;
- inspect evidence.

## Updated Chat

Project Chat now retrieves `PROCESS PROFILES` and prioritizes them for workflow/process questions such as:

- Как происходит Funding?
- Какие этапы проходит Merchant?
- Кто участвует в Underwriting?
- Какие правила есть в Repayment?

## Updated Project Summary

Project Summary Builder now uses:

```text
Actors
Processes
Domain Objects
Ontology
Relationships
Facts
```

## Recommended build order

```text
1. Canonical Facts
2. Entities
3. Relationships
4. Ontology
5. Domain Model
6. Actors
7. Processes
8. Project Summary
```

## Run

```powershell
python -m streamlit run app.py
```

Then open:

```text
Project Model → Processes → Build / Refresh Processes
```

## Commit

```powershell
git add .
git commit -m "Commit 37 - Add business process intelligence"
```
