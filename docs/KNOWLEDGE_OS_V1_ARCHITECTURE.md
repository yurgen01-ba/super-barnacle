# Knowledge OS v1 Architecture

## Product concept

Project Brain is a Knowledge Operating System for projects, not a chat over files.

The core user-visible unit after processing is an **Extraction**. Each Extraction produces **Artifacts** that can be opened, searched, compared, downloaded and traced back to source.

## Main entities

```text
Project
 ├── Sources
 ├── Extractions
 │      ├── Artifacts
 │      ├── Timeline
 │      ├── Statistics
 │      └── Debug
 ├── Current Project Model
 ├── Knowledge Timeline
 └── Chat
```

## Extraction

An Extraction is a single processing run over one or more sources.

Examples:
- meeting video processing;
- Slack import;
- Jira PDF import;
- Confluence page import.

Fields:
- id
- project_id
- source_id
- source_name
- source_type
- status
- started_at
- finished_at
- duration_seconds
- artifact_count
- statistics
- metadata

## Artifact

An Artifact is a concrete generated output.

Examples:
- Transcript
- Clean Transcript
- Screen Timeline
- Extracted Facts
- Rejected Facts
- Ontology Mapping
- Project Model Snapshot
- Project Summary
- Summary Diff
- Prompt
- Final Answer
- Logs

Fields:
- id
- extraction_id
- project_id
- artifact_type
- title
- description
- content
- format
- status
- created_at
- metadata

## UI navigation

```text
Dashboard
Sources
Extractions
Project Model
Knowledge Timeline
Chat
Settings
```

## Extraction Report UX

After a job completes, instead of a minimal "Job result is available", show:

```text
Knowledge Extraction Report

Source: Lecture_01.mp4
Status: Completed
Generated artifacts: 9

Human-readable artifacts:
- Transcript
- Clean Transcript
- Screen Timeline

Knowledge:
- Extracted Facts
- Rejected Facts
- Ontology Mapping
- Project Model
- Project Summary
- Summary Diff

Developer:
- Prompt
- Reasoning Context
- Logs
```

## Explainability rule

Every answer should be traceable:

```text
Answer
 ↓
Evidence
 ↓
Fact
 ↓
Transcript sentence / frame / source
 ↓
Original file
```

## Implementation roadmap

| Commit | Name |
|---|---|
| 139 | Knowledge OS v1 Architecture |
| 140 | Extraction Model |
| 141 | Artifact Registry |
| 142 | Artifact Service |
| 143 | Transcript Artifact Builder |
| 144 | Screen Timeline Artifact Builder |
| 145 | Knowledge Artifact Builder |
| 146 | Ontology Artifact Builder |
| 147 | Project Model Artifact Builder |
| 148 | Extraction Report UI |
| 149 | Artifact Cards UI |
| 150 | Transcript Viewer |
| 151 | Screen Timeline Viewer |
| 152 | Knowledge Viewer |
| 153 | Ontology Viewer |
| 154 | Project Model Viewer |
| 155 | Summary Diff Viewer |
| 156 | Extraction History |
| 157 | Developer Debug Panel |
| 158 | Artifact Download Manager |
| 159 | Job Result Integration |
| 160 | Knowledge Artifacts Navigation |
