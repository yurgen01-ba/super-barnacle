# Knowledge Debugger Workflow

Use Knowledge Debugger to locate where answer quality breaks.

1. `raw_transcript_segment` — check Whisper.
2. `clean_transcript_segment` — check cleanup.
3. `accepted_facts` — check fact extraction.
4. `rejected_facts` — check confidence/ontology filtering.
5. `ontology_trace` — check canonical mapping.
6. `project_model_snapshot` — check model update.
7. `reasoning_context` — check planner/evidence.
8. `final_prompt` — check prompt constraints.
9. `final_answer` — check LLM hallucination.

Typical fixes:
- Bad raw transcript: improve audio/model/language/glossary.
- Bad facts: tighten extractor prompt or confidence gate.
- Empty ontology: extend Domain Dictionary aliases.
- Bad context: adjust Query Planner or Evidence Ranking.
- Bad answer with good context: lower temperature or strengthen prompt.
