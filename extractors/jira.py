from ai.jira_extractor import extract_jira_knowledge
from utils.text import chunk_text


def process_jira_text(text: str, progress_callback=None, **extractor_options):
    chunks = chunk_text(text, max_chars=10000)
    all_items = []
    errors = []

    for idx, chunk in enumerate(chunks, start=1):
        if progress_callback:
            progress_callback({"event": "chunk_started", "current": idx, "total": len(chunks)})
        try:
            items = extract_jira_knowledge(
                chunk,
                source=f"jira_text:chunk_{idx}",
                **extractor_options,
            )
            all_items.extend(items)
            if progress_callback:
                progress_callback({
                    "event": "chunk_completed", "current": idx, "total": len(chunks),
                    "items_count": len(items),
                })
        except Exception as e:
            errors.append(f"Jira text chunk {idx} failed: {repr(e)}")
            if progress_callback:
                progress_callback({
                    "event": "chunk_failed", "current": idx, "total": len(chunks),
                    "error": str(e),
                })

    return {
        "chunks_count": len(chunks),
        "items": all_items,
        "errors": errors,
    }

