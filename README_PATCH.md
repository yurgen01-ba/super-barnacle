# Project Brain Cost + Progress Patch

This patch fixes three product issues:

1. No visible progress for large files
2. Reports are too detailed and just retell source files
3. Reports are too expensive

## 1. Replace report generator

Replace:

```text
ai/report_generator.py
```

with:

```text
report_generator_replacement.py
```

What changes:
- compact memory is sent to Claude instead of full memory;
- executive summary is default;
- report length is capped;
- report stops retelling every Jira ticket/video transcript.

## 2. Replace Report tab in app.py

Find the current:

```python
with tab_report:
    ...
```

Replace that whole block with:

```text
app_report_block_replacement.py
```

## 3. Add progress indicators

Use examples from:

```text
progress_patterns.py
```

Recommended first:
- update Jira PDF button first;
- then video button;
- Slack/Jira text are smaller, spinner is enough.

## Expected cost reduction

The expensive part was sending too much Project Memory into the report prompt.

This patch:
- limits items per type;
- truncates each item;
- reduces max_tokens;
- defaults to executive mode.

Expected report cost should drop significantly, often by 3-10x depending on Memory size.

## Important

Extraction may still be expensive if you process large PDFs/videos. Report cost and extraction cost are separate.

Next optimization should be:
- use Haiku/Fable for extraction if available and cheaper;
- extract less from raw files;
- store source summaries separately;
- add "Only extract top N project facts" mode.
