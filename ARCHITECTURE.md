# Project Brain Architecture

Project Brain is an AI Business Analyst platform that continuously builds and maintains a living model of a software project.

It is not a chatbot, not a document search tool, and not just RAG. It is a Project Knowledge Graph with an AI reasoning layer on top.

## Core principle

Everything important in the project should become a structured, traceable knowledge object.

Documents, meetings, Slack messages, Jira tickets and Confluence pages are sources. They are not the final product. The final product is a living Project Model.

## Architecture layers

```text
Sources
  ↓
Ingestion
  ↓
Knowledge Extraction
  ↓
Knowledge Graph
  ↓
Project Model
  ↓
Reasoning Layer
  ↓
User Workspace
```

## Sources

Supported and planned sources:

```text
Meetings
Video recordings
Screen recordings
Slack
Jira
Confluence
PDF
Images
Emails
API specs
Database schemas
Figma
Git repositories
```

## Ingestion layer

The ingestion layer converts raw source content into normalized intermediate data.

Examples:

```text
Video → frames + transcript
Audio → transcript
Slack export → message chunks
Jira → issue records
Confluence → article text
PDF → text + images
Screenshot → visual observations
```

The ingestion layer should not decide what is true. It only prepares source material for extraction.

## Knowledge extraction layer

The extraction layer creates structured knowledge from normalized source data.

Existing and planned extracted objects:

```text
Facts
Entities
Actors
Processes
Rules
Requirements
Decisions
Risks
Integrations
APIs
Glossary terms
Timeline events
Metrics
```

## Knowledge Graph layer

The Knowledge Graph is the core of the product.

It stores:

```text
Knowledge Nodes
Relationships
Evidence
Confidence
Status
Versions
Provenance
```

A node can represent:

```text
Fact
Entity
Actor
Process
Process Step
Business Rule
Requirement
Decision
Risk
API
Integration
Screen
Database Table
Metric
Artifact
Source Fragment
Hypothesis
```

A relationship can represent:

```text
participates_in
depends_on
implements
discussed_in
contradicts
supersedes
caused_by
affects
tested_by
documented_by
owned_by
created_by
```

## Project Model layer

The Project Model is a curated view of the Knowledge Graph and the single source of truth for AI responses and artifact generation.

## Reasoning layer

The reasoning layer should work before LLM generation.

It contains:

```text
Intent Detection
Planner
Graph Retriever
Evidence Ranking
Confidence Scoring
Coverage Analysis
Contradiction Detection
Impact Analysis
Artifact Planning
```

The LLM should receive structured context from the Project Model, not random chunks.

## User workspace

Current UI direction:

```text
Left: Project / Sources navigation
Center: Dashboard and workspace
Right: AI Assistant
```

Important UX decisions:

- AI Assistant is always available.
- Data upload is available directly from Dashboard.
- Artifacts are generated from AI Assistant.
- Project Model is hidden as an advanced/debug mode.
- Multi-project support is part of the product foundation.

## Near-term architecture direction

The next major technical step is Project Knowledge Graph Engine:

```text
KnowledgeNode
KnowledgeRelationship
Evidence
Confidence
Status
Versioning
Graph Repository
Graph Retriever
```
