import json
import urllib.error
import urllib.request


def check_ollama_text_model(
    host: str = "http://localhost:11434",
    model: str | None = None,
    timeout_seconds: int = 10,
):
    url = host.rstrip("/") + "/api/tags"

    try:
        request = urllib.request.Request(url=url, method="GET")

        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            data = json.loads(response.read().decode("utf-8"))

        models = [item.get("name") or item.get("model") for item in data.get("models", [])]

        return {
            "ok": True,
            "host": host,
            "models": models,
            "model_available": model in models if model else None,
            "error": None,
        }

    except Exception as exc:
        return {
            "ok": False,
            "host": host,
            "models": [],
            "model_available": False if model else None,
            "error": repr(exc),
        }

