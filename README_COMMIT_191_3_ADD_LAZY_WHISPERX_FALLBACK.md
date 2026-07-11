# Commit 191.3 — Add lazy WhisperX backend fallback

Prevents application startup failure when WhisperX or one of its native
dependencies is missing or incompatible. The backend initializes only when
audio processing starts and falls back to legacy OpenAI Whisper when needed.

## Git commands

```powershell
git add transcription/audio_transcriber_factory.py transcription/audio_intelligence_service.py README_COMMIT_191_3_ADD_LAZY_WHISPERX_FALLBACK.md
git commit -m "Commit 191.3 - Add lazy WhisperX backend fallback"
```
