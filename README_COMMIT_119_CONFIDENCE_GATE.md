# Commit 119 — Confidence Gate

## Goal

Drop low-confidence and ontology-unknown facts before they enter the graph.

## Changed

```text
quality/__init__.py
quality/confidence_gate.py
pipeline/canonical_facts_pipeline.py
```

## Commit

```powershell
git add quality/__init__.py quality/confidence_gate.py pipeline/canonical_facts_pipeline.py README_COMMIT_119_CONFIDENCE_GATE.md
git commit -m "Commit 119 - Add confidence gate before graph ingestion"
```
