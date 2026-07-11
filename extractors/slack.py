from ai.extractor import extract_knowledge
from parsers.slack_chunker import chunk_slack_messages, chunk_to_text


def process_slack_text(text: str, chunk_size: int = 12):
    chunks = chunk_slack_messages(text, chunk_size=chunk_size)
    all_items = []
    errors = []

    for idx, chunk in enumerate(chunks, start=1):
        chunk_text = chunk_to_text(chunk)
        try:
            items = extract_knowledge(chunk_text, source=f"slack_paste:chunk_{idx}")
            all_items.extend(items)
        except Exception as e:
            errors.append(f"Slack chunk {idx} failed: {repr(e)}")

    return {
        "chunks_count": len(chunks),
        "items": all_items,
        "errors": errors,
    }

