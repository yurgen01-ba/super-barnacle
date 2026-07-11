# WhisperX installation compatibility

WhisperX 3.8.6 requires Python >=3.10 and <3.14.

Do not pin `faster-whisper`, `ctranslate2`, `pyannote.audio`, `torch`,
`torchaudio`, or `torchvision` separately in `requirements-whisperx.txt`.
WhisperX already declares compatible versions for those packages.

Use Python 3.12 for the dedicated WhisperX environment.
