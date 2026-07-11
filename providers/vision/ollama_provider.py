import base64
import json
import re
import socket
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Callable, List

from providers.vision.base import VisionProvider


VisionProgressCallback = Callable[[dict], None]


class OllamaVisionProvider(VisionProvider):
    def __init__(
        self,
        model: str = "qwen2.5vl:3b",
        host: str = "http://localhost:11434",
        batch_size: int = 1,
        timeout_seconds: int = 60,
    ):
        self.model = model
        self.host = host.rstrip("/")
        self.batch_size = 1  # Safe mode: always one frame at a time.
        self.timeout_seconds = max(10, int(timeout_seconds))

    def analyze_frames(
        self,
        frame_paths: List[str],
        source: str,
        progress_callback: VisionProgressCallback | None = None,
    ) -> list[dict]:
        if not frame_paths:
            return []

        all_items = []
        total = len(frame_paths)

        for frame_index, frame_path in enumerate(frame_paths, start=1):
            frame_source = f"{source}:frame_{frame_index}"
            started_at = time.time()

            self._emit(
                progress_callback,
                {
                    "event": "frame_started",
                    "current": frame_index,
                    "total": total,
                    "source": frame_source,
                    "model": self.model,
                },
            )

            try:
                raw_response = self._post_ollama_chat(
                    content=self._build_prompt(frame_source),
                    image_paths=[frame_path],
                )

                parsed = self._safe_json_loads_or_observation(
                    raw_response,
                    source=frame_source,
                )

                frame_items = self._normalize_items(parsed, source=frame_source)
                all_items.extend(frame_items)

                self._emit(
                    progress_callback,
                    {
                        "event": "frame_completed",
                        "current": frame_index,
                        "total": total,
                        "source": frame_source,
                        "model": self.model,
                        "items_count": len(frame_items),
                        "elapsed_seconds": round(time.time() - started_at, 1),
                    },
                )

            except Exception as exc:
                error_item = {
                    "type": "screen_observation",
                    "title": "Screen analysis failed for frame",
                    "content": (
                        f"Local Ollama vision analysis failed for this frame. "
                        f"Reason: {repr(exc)}"
                    )[:1400],
                    "source": frame_source,
                }
                all_items.append(error_item)

                self._emit(
                    progress_callback,
                    {
                        "event": "frame_failed",
                        "current": frame_index,
                        "total": total,
                        "source": frame_source,
                        "model": self.model,
                        "items_count": 1,
                        "error": repr(exc),
                        "elapsed_seconds": round(time.time() - started_at, 1),
                    },
                )

        return all_items

    @staticmethod
    def _emit(progress_callback: VisionProgressCallback | None, event: dict):
        if progress_callback:
            try:
                progress_callback(event)
            except Exception:
                # Progress callback must never break processing.
                pass

    def _build_prompt(self, source: str) -> str:
        return f"""
You are a visual project knowledge extractor.

Analyze this screenshot from a meeting video and extract useful project knowledge.

Return ONLY a valid JSON array:

[
  {{
    "type": "screen_observation",
    "title": "short concrete title",
    "content": "specific useful information visible on screen",
    "source": "{source}"
  }}
]

Allowed type values:
- screen_observation
- requirement
- feature
- business_rule
- risk
- question
- integration
- api
- ui_screen
- diagram
- error
- glossary

Extract useful visible information:
- Jira issue info
- Confluence page content
- UI fields/buttons/flows
- diagrams
- API/Swagger info
- terminal errors
- code/IDE observations
- tables, forms, statuses, business terms

Rules:
- Do not invent details.
- Return [] if unreadable or irrelevant.
- Keep output concise.
- Return ONLY JSON.
"""

    def _post_ollama_chat(self, content: str, image_paths: List[str]) -> str:
        url = self.host + "/api/chat"
        images = [
            base64.b64encode(Path(path).read_bytes()).decode("utf-8")
            for path in image_paths
        ]

        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": content,
                    "images": images,
                }
            ],
            "options": {
                "num_predict": 900,
                "temperature": 0.1,
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
                f"Ollama vision request timed out after {self.timeout_seconds}s. "
                f"Try fewer frames, qwen2.5vl:3b, or disable screen analysis."
            ) from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(
                f"Could not connect to Ollama at {self.host}. "
                f"Make sure Ollama is installed/running and model is pulled. "
                f"Model: {self.model}. Details: {exc}"
            ) from exc

    @staticmethod
    def _extract_json_array(text: str) -> str:
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
        cleaned = re.sub(r"```$", "", cleaned).strip()

        start = cleaned.find("[")
        end = cleaned.rfind("]")

        if start == -1 or end == -1 or end <= start:
            raise ValueError(f"No JSON array found. Preview: {cleaned[:500]}")

        return cleaned[start:end + 1]

    def _safe_json_loads_or_observation(self, text: str, source: str):
        try:
            return json.loads(self._extract_json_array(text))
        except Exception:
            if not text.strip():
                return []
            return [{
                "type": "screen_observation",
                "title": "Raw visual analysis",
                "content": text.strip()[:1400],
                "source": source,
            }]

    @staticmethod
    def _normalize_items(data, source: str):
        if not isinstance(data, list):
            return []

        normalized = []

        for item in data:
            if not isinstance(item, dict):
                continue

            title = str(item.get("title") or "Untitled").strip()
            content = str(item.get("content") or "").strip()

            if not content:
                continue

            normalized.append({
                "type": str(item.get("type") or "screen_observation")[:80],
                "title": title[:220],
                "content": content[:1400],
                "source": str(item.get("source") or source),
            })

        return normalized

