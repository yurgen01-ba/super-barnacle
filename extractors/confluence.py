from ai.confluence_extractor import extract_confluence_knowledge
from utils.text import chunk_text


def process_confluence_text(text: str, title: str = "Confluence article", progress_callback=None, **extractor_options):
    chunks = chunk_text(text, max_chars=10000)
    all_items = []
    errors = []

    for idx, chunk in enumerate(chunks, start=1):
        if progress_callback:
            progress_callback({"event": "chunk_started", "current": idx, "total": len(chunks)})
        try:
            items = extract_confluence_knowledge(
                chunk,
                source=f"confluence:{title}:chunk_{idx}",
                **extractor_options,
            )
            all_items.extend(items)
            if progress_callback:
                progress_callback({"event": "chunk_completed", "current": idx, "total": len(chunks)})
        except Exception as e:
            errors.append(f"Confluence chunk {idx} failed: {repr(e)}")
            if progress_callback:
                progress_callback({"event": "chunk_failed", "current": idx, "total": len(chunks), "error": str(e)})

    return {
        "title": title,
        "chunks_count": len(chunks),
        "items": all_items,
        "errors": errors,
        "text": text,
    }

