# Persistent Knowledge Extraction Jobs

## Problem

Before this change, knowledge extraction could be started directly inside a Streamlit page render.

That means:

```text
click button
↓
pipeline runs inside current page render
↓
user switches tab
↓
Streamlit reruns page
↓
process state is lost
```

## New model

Extraction must be started as a background job:

```text
UI
↓
KnowledgeExtractionJobService
↓
BackgroundJobExecutor
↓
Pipeline / extractor
↓
ProgressRepository
↓
UI reconnects by job_id
```

## How to migrate existing UI code

Do not do this:

```python
if st.button("Extract"):
    run_extraction()
```

Do this:

```python
from ui.persistent_extraction import start_or_attach_knowledge_extraction

start_or_attach_knowledge_extraction(
    run_extraction,
    button_label="Start knowledge extraction",
    metadata={"source": "meeting"},
)
```

## If your extraction function supports progress

```python
def run_extraction(progress=None):
    if progress:
        progress.update(0.1, "transcription", "Transcribing video")
    ...
    if progress:
        progress.update(0.7, "fact_extraction", "Extracting facts")
```

## If your extraction function does not support progress

It will still run in the background.
The job will show started/completed status.

## How to render current job status

```python
from ui.persistent_extraction import render_knowledge_extraction_status

render_knowledge_extraction_status()
```

## Rule

Long-running operations must not run directly inside Streamlit render functions.

They must run via:

```python
KnowledgeExtractionJobService
```
