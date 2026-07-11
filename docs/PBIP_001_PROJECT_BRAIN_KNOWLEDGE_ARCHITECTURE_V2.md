# PBIP-001 — Project Brain Knowledge Architecture v2.0

## Goal

Move Project Brain from "RAG with graph" to a Knowledge OS architecture.

## Target architecture

```text
Sources → Raw Knowledge → Canonical Knowledge → Project Knowledge → Retrieval + Reasoning → Answer
```

## Core principle

Canonical knowledge and Project Model become the source of truth. The Project Graph becomes a navigable representation, not the only truth layer.

## Knowledge lifecycle

```text
RAW → EXTRACTED → CANONICAL → CONNECTED → VERIFIED → SUMMARIZED → SUPERSEDED / ARCHIVED
```

## Commit roadmap

| Commit | Name | Purpose |
|---|---|---|
| 122 | Architecture Refactor PRD | Define v2.0 target architecture |
| 123 | Project Model Core | Add durable ProjectModel |
| 124 | Knowledge Evolution Engine | Add fact lifecycle/versioning |
| 125 | Incremental Summary Engine | Update summary incrementally |
| 126 | Conflict Detection Engine | Detect contradictory facts |
| 127 | Evidence Ranking Engine | Rank supporting evidence |
| 128 | Query Planner | Plan retrieval by intent |
| 129 | Reasoning Pipeline | Summary + evidence + model → answer |
| 130 | Graph QA v3 | Route chat through Knowledge OS pipeline |
