from ai.fact_extractor import extract_canonical_facts
from repositories.fact_repository import FactRepository


class FactBuilder:
    def __init__(
        self,
        model: str = "qwen2.5:7b",
        host: str = "http://localhost:11434",
        timeout_seconds: int = 240,
    ):
        self.model = model
        self.host = host
        self.timeout_seconds = timeout_seconds
        self.fact_repository = FactRepository()

    def extract_facts(
        self,
        text: str,
        source: str,
        source_type: str = "unknown",
    ):
        return extract_canonical_facts(
            text=text,
            source=source,
            source_type=source_type,
            model=self.model,
            host=self.host,
            timeout_seconds=self.timeout_seconds,
        )

    def build_and_save_facts(
        self,
        text: str,
        source: str,
        source_type: str = "unknown",
    ):
        facts = self.extract_facts(
            text=text,
            source=source,
            source_type=source_type,
        )

        save_result = self.fact_repository.save_facts(facts)

        return {
            "facts": facts,
            "save_result": save_result,
        }

