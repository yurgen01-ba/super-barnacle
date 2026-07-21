import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
DB_PATH = os.getenv("PROJECT_BRAIN_DB_PATH", "data/project.db")

CLAUDE_EXTRACTOR_MODEL = os.getenv("CLAUDE_EXTRACTOR_MODEL", "claude-sonnet-4-6")
CLAUDE_REPORT_MODEL = os.getenv("CLAUDE_REPORT_MODEL", "claude-sonnet-4-6")
WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL_NAME", "large-v3")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cuda")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "float16")

AUDIO_TRANSCRIPTION_BACKEND = os.getenv("AUDIO_TRANSCRIPTION_BACKEND", "whisperx")

WHISPERX_MODEL_NAME = os.getenv("WHISPERX_MODEL_NAME", "large-v3")

WHISPERX_DEVICE = os.getenv("WHISPERX_DEVICE", "cuda")

WHISPERX_COMPUTE_TYPE = os.getenv("WHISPERX_COMPUTE_TYPE", "float16")

WHISPERX_BATCH_SIZE = os.getenv("WHISPERX_BATCH_SIZE", "4")

WHISPERX_LANGUAGE = os.getenv("WHISPERX_LANGUAGE") or None

WHISPERX_INITIAL_PROMPT = os.getenv(
    "WHISPERX_INITIAL_PROMPT",
    (
        "Русская техническая встреча. Термины: Jira, Jira task, title, "
        "in scope of this task, info panel, summary, accounts, OrgMeter, "
        "Confluence, white label, field scope. Пример фразы: «Давай без "
        "этих titles in scope of this task. Берем отсюда summary, например "
        "accounts»."
    ),
)

WHISPERX_HOTWORDS = os.getenv(
    "WHISPERX_HOTWORDS",
    (
        "Jira, Jira task, title, in scope of this task, info panel, "
        "summary, accounts, OrgMeter, Confluence, white label, field scope"
    ),
)

WHISPERX_VAD_ONSET = os.getenv("WHISPERX_VAD_ONSET", "0.35")

WHISPERX_VAD_OFFSET = os.getenv("WHISPERX_VAD_OFFSET", "0.25")

WHISPERX_ENABLE_ALIGNMENT = os.getenv("WHISPERX_ENABLE_ALIGNMENT", "true")

WHISPERX_ENABLE_DIARIZATION = os.getenv("WHISPERX_ENABLE_DIARIZATION", "true")
