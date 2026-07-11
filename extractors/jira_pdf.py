from pypdf import PdfReader

from ai.jira_extractor import extract_jira_knowledge
from utils.text import chunk_text


def extract_text_from_pdf(uploaded_file) -> str:
    reader = PdfReader(uploaded_file)
    pages = []

    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            pages.append(f"\n\n[PDF page {page_index}]\n{text}")

    return "\n\n".join(pages).strip()


def process_jira_pdfs(uploaded_files):
    results = []

    for uploaded_file in uploaded_files:
        text = extract_text_from_pdf(uploaded_file)

        if not text:
            results.append({
                "file_name": uploaded_file.name,
                "text": "",
                "chunks_count": 0,
                "items": [],
                "warning": "No text extracted. This may be a scanned PDF and may require OCR.",
                "errors": [],
                "debug": {
                    "extractor": "jira_extractor_with_fallback",
                    "text_length": 0,
                    "items_count": 0,
                },
            })
            continue

        chunks = chunk_text(text, max_chars=10000)
        all_items = []
        errors = []

        for idx, chunk in enumerate(chunks, start=1):
            try:
                items = extract_jira_knowledge(
                    chunk,
                    source=f"jira_pdf:{uploaded_file.name}:chunk_{idx}",
                )
                all_items.extend(items)
            except Exception as e:
                errors.append(f"PDF chunk {idx} failed: {repr(e)}")

        results.append({
            "file_name": uploaded_file.name,
            "text": text,
            "chunks_count": len(chunks),
            "items": all_items,
            "warning": None if all_items else (
                "No knowledge items extracted from this PDF. "
                "The PDF text may be too noisy, empty, or not Jira-like enough."
            ),
            "errors": errors,
            "debug": {
                "extractor": "jira_extractor_with_fallback",
                "text_length": len(text),
                "items_count": len(all_items),
            },
        })

    return results

