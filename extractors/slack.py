from ai.extractor import extract_knowledge
from parsers.slack_chunker import chunk_slack_messages, chunk_to_text


def process_slack_text(text: str, chunk_size: int = 12, progress_callback=None, **extractor_options):
    chunks = chunk_slack_messages(text, chunk_size=chunk_size)
    all_items = []
    errors = []

    for idx, chunk in enumerate(chunks, start=1):
        chunk_text = chunk_to_text(chunk)
        if progress_callback:
            progress_callback({"event": "chunk_started", "current": idx, "total": len(chunks)})
        try:
            items = extract_knowledge(
                chunk_text, source=f"slack_paste:chunk_{idx}", **extractor_options
            )
            all_items.extend(items)
            if progress_callback:
                progress_callback({"event": "chunk_completed", "current": idx, "total": len(chunks)})
        except Exception as e:
            errors.append(f"Slack chunk {idx} failed: {repr(e)}")
            if progress_callback:
                progress_callback({"event": "chunk_failed", "current": idx, "total": len(chunks), "error": str(e)})

    return {
        "chunks_count": len(chunks),
        "items": all_items,
        "errors": errors,
    }

