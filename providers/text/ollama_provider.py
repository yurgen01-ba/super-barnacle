import json
import socket
import urllib.error
import urllib.request

from providers.text.base import TextProvider


class OllamaTextProvider(TextProvider):
    def __init__(
        self,
        model: str = "qwen2.5:7b",
        host: str = "http://localhost:11434",
        timeout_seconds: int = 180,
        temperature: float = 0.1,
        num_predict: int = 2500,
    ):
        self.model = model
        self.host = host.rstrip("/")
        self.timeout_seconds = max(10, int(timeout_seconds))
        self.temperature = temperature
        self.num_predict = num_predict

    def generate(self, prompt: str) -> str:
        url = self.host + "/api/chat"

        payload = {
            "model": self.model,
            "stream": False,
            "messages": [{"role": "user", "content": prompt}],
            "options": {
                "temperature": self.temperature,
                "num_predict": self.num_predict,
            },
        }

        request = urllib.request.Request(
            url=url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                data = json.loads(response.read().decode("utf-8"))
                return data.get("message", {}).get("content", "")
        except socket.timeout as exc:
            raise TimeoutError(
                f"Ollama text request timed out after {self.timeout_seconds}s. "
                f"Try qwen2.5:3b or fewer transcript chunks."
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Could not connect to Ollama at {self.host}. "
                f"Make sure Ollama is running and model is pulled. "
                f"Model: {self.model}. Details: {exc}"
            ) from exc

    def stream(self, prompt: str):
        """Yield Ollama tokens as they arrive so the UI never looks frozen."""
        url = self.host + "/api/chat"
        payload = {
            "model": self.model,
            "stream": True,
            "messages": [{"role": "user", "content": prompt}],
            "options": {
                "temperature": self.temperature,
                "num_predict": self.num_predict,
            },
        }
        request = urllib.request.Request(
            url=url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                for raw_line in response:
                    if not raw_line.strip():
                        continue
                    data = json.loads(raw_line.decode("utf-8"))
                    content = data.get("message", {}).get("content", "")
                    if content:
                        yield content
                    if data.get("done"):
                        break
        except socket.timeout as exc:
            raise TimeoutError(
                f"Ollama text stream timed out after {self.timeout_seconds}s."
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Could not connect to Ollama at {self.host}. Model: {self.model}. Details: {exc}"
            ) from exc

