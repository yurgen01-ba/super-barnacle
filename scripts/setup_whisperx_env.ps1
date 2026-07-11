param(
    [string]$Python312Path = "",
    [string]$VenvPath = ".venv-whisperx"
)

$ErrorActionPreference = "Stop"

function Resolve-Python312 {
    param([string]$ExplicitPath)

    if ($ExplicitPath -and (Test-Path $ExplicitPath)) {
        return (Resolve-Path $ExplicitPath).Path
    }

    try {
        $candidate = & py -3.12 -c "import sys; print(sys.executable)" 2>$null
        if ($LASTEXITCODE -eq 0 -and $candidate) {
            return $candidate.Trim()
        }
    } catch {}

    $commonPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "C:\Python312\python.exe"
    )

    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            return $path
        }
    }

    throw @"
Python 3.12 was not found.

Install Python 3.12, then rerun either:

  powershell -ExecutionPolicy Bypass -File scripts\setup_whisperx_env.ps1

or:

  powershell -ExecutionPolicy Bypass -File scripts\setup_whisperx_env.ps1 -Python312Path "C:\path\to\python.exe"
"@
}

$python312 = Resolve-Python312 -ExplicitPath $Python312Path
Write-Host "Using Python: $python312"

if (Test-Path $VenvPath) {
    Write-Host "Removing existing environment: $VenvPath"
    Remove-Item -Recurse -Force $VenvPath
}

& $python312 -m venv $VenvPath

$venvPython = Join-Path $VenvPath "Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    throw "Virtual environment Python was not created: $venvPython"
}

& $venvPython -m pip install --upgrade pip setuptools wheel

if (Test-Path "requirements.txt") {
    Write-Host "Installing Project Brain base requirements..."
    & $venvPython -m pip install -r requirements.txt
}

Write-Host "Installing WhisperX..."
& $venvPython -m pip install -r requirements-whisperx.txt

Write-Host "Checking dependency consistency..."
& $venvPython -m pip check
if ($LASTEXITCODE -ne 0) {
    throw "pip check failed. See dependency errors above."
}

Write-Host "Validating imports..."
& $venvPython -c "import sys, torch, whisperx; print('Python:', sys.version); print('WhisperX: OK'); print('Torch:', torch.__version__); print('Torch CUDA:', torch.version.cuda); print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU')"

Write-Host ""
Write-Host "WhisperX environment is ready."
Write-Host "Run Project Brain with:"
Write-Host "  .\$VenvPath\Scripts\python.exe -m streamlit run app.py"
