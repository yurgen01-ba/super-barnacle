# Commit 24 — Project Chat

## Goal

Add a chat window for asking questions about the project.

## Added

```text
repositories/chat_context_repository.py
ai/project_chat.py
ui/project_chat.py
APP_CHANGE.md
```

## Behavior

Project Chat:
- searches Project Memory;
- searches source chunks;
- sends retrieved context to local Ollama text model;
- answers with citations like `[memory:12]` or `[chunk:44]`;
- shows context used;
- keeps chat history in Streamlit session state.

## Apply

Copy files:

```text
repositories/chat_context_repository.py
ai/project_chat.py
ui/project_chat.py
```

Then update `app.py` using `APP_CHANGE.md`.

Commit:

```powershell
git add .
git commit -m "Commit 24 - Add Project Chat"
```
