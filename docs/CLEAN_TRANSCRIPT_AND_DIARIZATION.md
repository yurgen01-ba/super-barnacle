# Clean Transcript + Speaker Diarization

Pipeline:

Audio → Whisper → loop cleanup → terminology resolver → sentence repair → boundary stitching → pyannote diarization → speaker utterances → knowledge extraction.

Install optional diarization:

```powershell
python -m pip install -r requirements-diarization.txt
$env:HUGGINGFACE_TOKEN="<your-token>"
```

Without pyannote or a token, the pipeline falls back to a cleaned non-diarized transcript.
