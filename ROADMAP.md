# Project Brain Roadmap

## Completed foundation

Sprint 1 delivered:

```text
Meeting ingestion
Video/audio processing
Vision extraction
Local LLM support
Knowledge items
Canonical facts
Entities
Relationships
Ontology
Domain model
Actors
Processes
Project Summary
AI Chat
Confluence article generation
Jira draft generation
UI v2 shell
Dashboard source ingestion
Hidden Project Model
```

## Sprint 2 — Project Knowledge Graph

Goal: build the real core of Project Brain.

### Commit 41 — Architecture Docs

```text
ARCHITECTURE.md
VISION.md
DOMAIN_MODEL.md
ROADMAP.md
DECISIONS.md
UI_BACKLOG.md
```

### Commit 42 — Knowledge Node Schema

```text
knowledge_nodes
knowledge_relationships
knowledge_evidence
```

### Commit 43 — Knowledge Graph Repository

```text
KnowledgeNodeRepository
KnowledgeRelationshipRepository
GraphQueryService
```

### Commit 44 — Existing Model Migration

Map existing objects into Knowledge Nodes:

```text
Facts
Entities
Actors
Processes
Domain Objects
Relationships
```

### Commit 45 — Graph Retriever

Retrieve context through graph traversal instead of only text search.

### Commit 46 — AI Chat over Graph

AI Assistant uses:

```text
Intent
Graph Retriever
Project Model
Evidence
LLM Composer
```

## Sprint 3 — AI Analyst

Planned:

```text
Intent Planner
Requirement Generator
Contradiction Finder
Impact Analyzer
Traceability Finder
Risk Detector
Missing Knowledge Detector
Artifact Planner
```
