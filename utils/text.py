def chunk_text(text: str, max_chars: int = 8000, overlap_chars: int = 800):
    """
    Split text into chunks with a small overlap.

    Previous chunking used large non-overlapping 10k chunks. For long meetings,
    that often caused local LLM extraction to miss details near chunk borders and
    made prompts too dense. Smaller overlapping chunks increase extraction recall.
    """
    if not text or not text.strip():
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = []
    current_len = 0

    for paragraph in paragraphs:
        if current and current_len + len(paragraph) > max_chars:
            chunk = "\n\n".join(current).strip()
            if chunk:
                chunks.append(chunk)

            if overlap_chars > 0:
                overlap = chunk[-overlap_chars:]
                current = [overlap, paragraph]
                current_len = len(overlap) + len(paragraph)
            else:
                current = [paragraph]
                current_len = len(paragraph)
        else:
            current.append(paragraph)
            current_len += len(paragraph)

    if current:
        chunk = "\n\n".join(current).strip()
        if chunk:
            chunks.append(chunk)

    return chunks

