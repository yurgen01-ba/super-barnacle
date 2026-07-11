# Commit 193.2 — WhisperX Diarization Deep Diagnostics

Adds a complete stage-by-stage diarization report without exposing the
Hugging Face token itself.

## Captured diagnostics

- Hugging Face token presence and length;
- WhisperX, pyannote and PyTorch versions;
- CUDA runtime and GPU;
- audio loading time;
- ASR and alignment time;
- diarization pipeline loading time;
- diarization execution time;
- number of diarization turns;
- speaker labels found by pyannote;
- words and segments receiving speaker labels;
- full exception type, message and traceback.

The report is stored under:

```text
audio_intelligence.runtime.diarization_debug
```

## Git commands

```powershell
git add transcription/diarization_deep_diagnostics.py transcription/whisperx_transcriber.py ui_v2/components/diarization_debug_panel.py README_COMMIT_193_2_WHISPERX_DIARIZATION_DEEP_DIAGNOSTICS.md
git commit -m "Commit 193.2 - Add WhisperX diarization deep diagnostics"
```

## Validation

```powershell
.\.venv-whisperx\Scripts\python.exe -m py_compile transcription\diarization_deep_diagnostics.py transcription\whisperx_transcriber.py ui_v2\components\diarization_debug_panel.py

powershell -ExecutionPolicy Bypass -File scripts\run_project_brain_whisperx.ps1
```

After processing, open the `Audio Intelligence Runtime` artifact and inspect
the `runtime.diarization_debug` object.
