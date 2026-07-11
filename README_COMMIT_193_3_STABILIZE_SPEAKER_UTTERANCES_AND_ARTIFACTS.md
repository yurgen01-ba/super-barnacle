# Commit 193.3 — Stabilize Speaker Utterances and Propagate Diarization to Artifacts

## Changes

- reconstructs utterances from word-level speaker labels;
- smooths isolated one-word and sub-550 ms speaker flips;
- merges adjacent runs from the same speaker;
- preserves speaker timestamps;
- creates raw, clean and repaired speaker-aware transcript variants;
- displays diarization in Raw Transcript, Clean Transcript,
  Repaired Transcript and merged transcript artifacts;
- creates a structured Speaker Utterances JSON artifact.

## Git commands

```powershell
git add transcription/speaker_utterance_stabilizer.py transcription/audio_intelligence_service.py jobs/extraction_artifact_integration.py README_COMMIT_193_3_STABILIZE_SPEAKER_UTTERANCES_AND_ARTIFACTS.md
git commit -m "Commit 193.3 - Stabilize speaker utterances and propagate diarization to artifacts"
```

## Validation

```powershell
.\.venv-whisperx\Scripts\python.exe -m py_compile transcription\speaker_utterance_stabilizer.py transcription\audio_intelligence_service.py jobs\extraction_artifact_integration.py

powershell -ExecutionPolicy Bypass -File scripts\run_project_brain_whisperx.ps1
```

Reprocess the video after applying the commit. Existing artifacts are not
rewritten automatically.
