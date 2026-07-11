param(
    [string]$VenvPath = ".venv-whisperx",
    [string]$Model = "large-v3",
    [string]$Device = "cuda",
    [string]$ComputeType = "float16",
    [int]$BatchSize = 4
)

$ErrorActionPreference = "Stop"

$venvPython = Join-Path $VenvPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "WhisperX environment not found. Run scripts\setup_whisperx_env.ps1 first."
}

$env:AUDIO_TRANSCRIPTION_BACKEND = "whisperx"
$env:WHISPERX_MODEL_NAME = $Model
$env:WHISPERX_DEVICE = $Device
$env:WHISPERX_COMPUTE_TYPE = $ComputeType
$env:WHISPERX_BATCH_SIZE = "$BatchSize"
$env:WHISPERX_LANGUAGE = "ru"
$env:WHISPERX_ENABLE_ALIGNMENT = "true"
$env:WHISPERX_ENABLE_DIARIZATION = "true"

$dotenvHasToken = $false
if (Test-Path ".env") {
    $dotenvHasToken = [bool](
        Get-Content ".env" | Where-Object {
            $_ -match '^\s*(HUGGINGFACE_TOKEN|HF_TOKEN)\s*=\s*.+$'
        } | Select-Object -First 1
    )
}

if (-not $env:HUGGINGFACE_TOKEN -and -not $env:HF_TOKEN -and -not $dotenvHasToken) {
    Write-Warning "Hugging Face token is not set. Transcription/alignment can work, but diarization will be skipped."
}

& $venvPython -m streamlit run app.py
