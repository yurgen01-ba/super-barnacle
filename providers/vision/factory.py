from providers.vision.ollama_provider import OllamaVisionProvider


def create_vision_provider(
    provider_name: str = "ollama",
    model: str = "qwen2.5vl:3b",
    host: str = "http://localhost:11434",
    batch_size: int = 1,
    timeout_seconds: int = 60,
):
    if provider_name == "ollama":
        return OllamaVisionProvider(
            model=model,
            host=host,
            batch_size=batch_size,
            timeout_seconds=timeout_seconds,
        )

    raise ValueError(f"Unsupported vision provider: {provider_name}")

