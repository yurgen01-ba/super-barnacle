from dataclasses import dataclass
from config import (
    ANTHROPIC_API_KEY,
    DB_PATH,
    CLAUDE_EXTRACTOR_MODEL,
    CLAUDE_REPORT_MODEL,
    WHISPER_MODEL_NAME,
)


@dataclass(frozen=True)
class Settings:
    anthropic_api_key: str | None = ANTHROPIC_API_KEY
    db_path: str = DB_PATH
    claude_extractor_model: str = CLAUDE_EXTRACTOR_MODEL
    claude_report_model: str = CLAUDE_REPORT_MODEL
    whisper_model_name: str = WHISPER_MODEL_NAME
    app_title: str = "Project Brain"
    app_version: str = "3.0-commit1"


settings = Settings()

