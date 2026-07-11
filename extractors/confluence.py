from ai.confluence_extractor import extract_confluence_knowledge
from utils.text import chunk_text


def process_confluence_text(text: str, title: str = "Confluence article"):
    chunks = chunk_text(text, max_chars=10000)
    all_items = []
    errors = []

    for idx, chunk in enumerate(chunks, start=1):
        try:
            items = extract_confluence_knowledge(
                chunk,
                source=f"confluence:{title}:chunk_{idx}",
            )
            all_items.extend(items)
        except Exception as e:
            errors.append(f"Confluence chunk {idx} failed: {repr(e)}")

    return {
        "title": title,
        "chunks_count": len(chunks),
        "items": all_items,
        "errors": errors,
        "text": text,
    }

