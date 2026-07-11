# Commit 15 — Local Qwen2.5-VL Visual Pipeline via Ollama

## Goal

Replace expensive Claude Vision screen analysis with local Ollama/Qwen2.5-VL.

## Added

```text
ai/ollama_vision.py
```

## Replaced

```text
extractors/screen.py
extractors/meeting.py
ui/meetings.py
```

## Setup on Windows PowerShell

Install Ollama from:

```text
https://ollama.com/download
```

Then run:

```powershell
ollama pull qwen2.5vl:7b
```

Optional lighter model:

```powershell
ollama pull qwen2.5vl:3b
```

Check Ollama is running:

```powershell
ollama list
```

## Apply

Copy files into your project:

```text
ai/ollama_vision.py
extractors/screen.py
extractors/meeting.py
ui/meetings.py
```

Run:

```powershell
python -m streamlit run app.py
```

Commit:

```powershell
git add .
git commit -m "Commit 15 - Add local Qwen2.5-VL visual pipeline"
```
