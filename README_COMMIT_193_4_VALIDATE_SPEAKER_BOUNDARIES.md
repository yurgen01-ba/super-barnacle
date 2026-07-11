# Commit 193.4 — Validate Speaker Boundaries

Improves speaker attribution by validating every proposed speaker change
against word timing and linguistic boundaries.

## Rules

- reject a speaker change when the word gap is below 150 ms;
- require a sentence boundary for short 150–350 ms gaps;
- require a stable new speaker run;
- reject weak mid-sentence changes;
- protect phrases such as `in scope of this task`, `white label`,
  `Jira task`, `info panel` and other domain terms;
- preserve all boundary decisions in runtime diagnostics.

The debug report is available under:

```text
audio_intelligence.runtime.speaker_boundary_validation
```

## Git commands

```powershell
git add transcription/speaker_utterance_stabilizer.py transcription/audio_intelligence_service.py README_COMMIT_193_4_VALIDATE_SPEAKER_BOUNDARIES.md
git commit -m "Commit 193.4 - Validate speaker boundaries"
```

## Validation

```powershell
.\.venv-whisperx\Scripts\python.exe -m py_compile transcription\speaker_utterance_stabilizer.py transcription\audio_intelligence_service.py

powershell -ExecutionPolicy Bypass -File scripts\run_project_brain_whisperx.ps1
```

Reprocess the video. Existing transcript artifacts will not be updated
automatically.
