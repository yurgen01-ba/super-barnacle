# Commit 189.9 — Enable GPU Whisper Turbo

This hotfix enables the RTX GPU path for OpenAI Whisper and switches the default profile to `turbo`.

## Changes

- default model: `turbo`;
- model is loaded with `device=WHISPER_DEVICE`;
- default device: `cuda`;
- FP16 enabled;
- normal decoding reduced to `beam_size=3`, `best_of=3`;
- retry decoding reduced to `beam_size=5`, `best_of=5`;
- runtime guard fails clearly if CUDA was requested but Whisper loaded on CPU.

## Git commands

```powershell
git add config.py transcription/quality_config.py extractors/meeting.py README_COMMIT_189_9_ENABLE_GPU_WHISPER_TURBO.md
git commit -m "Commit 189.9 - Enable GPU Whisper Turbo"
```

## Validate

```powershell
python -m py_compile config.py transcription/quality_config.py extractors/meeting.py
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"
python -c "from config import WHISPER_MODEL_NAME, WHISPER_DEVICE; print(WHISPER_MODEL_NAME, WHISPER_DEVICE)"
python -m streamlit run app.py
```

During transcription:

```powershell
nvidia-smi -l 1
```
