import json
import re
from typing import Any


def extract_json_array_text(text: str) -> str:
    cleaned = (text or "").strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()

    start = cleaned.find("[")
    end = cleaned.rfind("]")

    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"No JSON array found. Preview: {cleaned[:500]}")

    return cleaned[start:end + 1]


def loads_json_array(text: str) -> list[Any]:
    array_text = extract_json_array_text(text)
    return json.loads(array_text)


def repair_json_array_text(text: str) -> str:
    """
    Lightweight repair for common local LLM JSON mistakes.

    It intentionally does not try to be a full JSON parser. It fixes only
    frequent generation issues we have observed:
    - markdown fences;
    - text before/after JSON;
    - trailing commas;
    - Python booleans/nulls;
    - missing comma between adjacent objects: } {;
    - newline-separated JSON objects without commas.
    """
    array_text = extract_json_array_text(text)

    repaired = array_text.strip()
    repaired = repaired.replace("\ufeff", "")
    repaired = re.sub(r",\s*([}\]])", r"\1", repaired)
    repaired = re.sub(r"\bNone\b", "null", repaired)
    repaired = re.sub(r"\bTrue\b", "true", repaired)
    repaired = re.sub(r"\bFalse\b", "false", repaired)
    repaired = re.sub(r"}\s*{", "}, {", repaired)
    repaired = re.sub(r"}\s*\n\s*{", "},\n{", repaired)

    return repaired


def safe_json_array_loads(text: str) -> list[Any]:
    try:
        return loads_json_array(text)
    except Exception:
        pass

    try:
        return json.loads(repair_json_array_text(text))
    except Exception:
        return []

