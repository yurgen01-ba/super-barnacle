from providers.text.ollama_provider import OllamaTextProvider


def create_text_provider(
    provider_name: str = "ollama",
    model: str = "qwen2.5:7b",
    host: str = "http://localhost:11434",
    timeout_seconds: int = 180,
    num_predict: int = 2500,
):
    if provider_name == "ollama":
        return OllamaTextProvider(
            model=model,
            host=host,
            timeout_seconds=timeout_seconds,
            num_predict=num_predict,
        )

    raise ValueError(f"Unsupported text provider: {provider_name}")

