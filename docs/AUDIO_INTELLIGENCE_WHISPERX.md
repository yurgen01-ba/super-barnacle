# Audio Intelligence Pipeline — WhisperX

WhisperX is open source and combines faster-whisper, VAD, forced alignment,
word timestamps and pyannote speaker diarization.

## Install

```powershell
python -m venv .venv-whisperx
.\.venv-whisperx\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-whisperx.txt
```

## Configure

```powershell
$env:AUDIO_TRANSCRIPTION_BACKEND="whisperx"
$env:WHISPERX_MODEL_NAME="turbo"
$env:WHISPERX_DEVICE="cuda"
$env:WHISPERX_COMPUTE_TYPE="float16"
$env:WHISPERX_BATCH_SIZE="8"
$env:HUGGINGFACE_TOKEN="hf_..."
```

The pipeline falls back to legacy OpenAI Whisper when WhisperX fails.
