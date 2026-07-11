from typing import List

from providers.vision.ollama_provider import OllamaVisionProvider


def analyze_screen_frames_with_ollama(
    frame_paths: List[str],
    source: str = "meeting_screen",
    model: str = "qwen2.5vl:7b",
    ollama_host: str = "http://localhost:11434",
    batch_size: int = 2,
):
    provider = OllamaVisionProvider(
        model=model,
        host=ollama_host,
        batch_size=batch_size,
    )

    return provider.analyze_frames(
        frame_paths=frame_paths,
        source=source,
    )

