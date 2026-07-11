from ai.jira_extractor import extract_jira_knowledge
from utils.text import chunk_text


def process_jira_text(text: str):
    chunks = chunk_text(text, max_chars=10000)
    all_items = []
    errors = []

    for idx, chunk in enumerate(chunks, start=1):
        try:
            items = extract_jira_knowledge(
                chunk,
                source=f"jira_text:chunk_{idx}",
            )
            all_items.extend(items)
        except Exception as e:
            errors.append(f"Jira text chunk {idx} failed: {repr(e)}")

    return {
        "chunks_count": len(chunks),
        "items": all_items,
        "errors": errors,
    }

