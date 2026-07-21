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


def process_jira_pdfs(uploaded_files, progress_callback=None, **extractor_options):
    results = []
    files_total = len(uploaded_files)

    for file_index, uploaded_file in enumerate(uploaded_files, start=1):
        if progress_callback:
            progress_callback({
                "event": "pdf_started", "current": file_index, "total": files_total,
                "file_name": uploaded_file.name,
            })
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
            if progress_callback:
                progress_callback({
                    "event": "pdf_completed", "current": file_index, "total": files_total,
                    "file_name": uploaded_file.name, "items_count": 0,
                })
            continue

        chunks = chunk_text(text, max_chars=10000)
        all_items = []
        errors = []

        for idx, chunk in enumerate(chunks, start=1):
            if progress_callback:
                progress_callback({
                    "event": "chunk_started", "file_current": file_index,
                    "file_total": files_total, "current": idx, "total": len(chunks),
                    "file_name": uploaded_file.name,
                })
            try:
                items = extract_jira_knowledge(
                    chunk,
                    source=f"jira_pdf:{uploaded_file.name}:chunk_{idx}",
                    **extractor_options,
                )
                all_items.extend(items)
                if progress_callback:
                    progress_callback({
                        "event": "chunk_completed", "file_current": file_index,
                        "file_total": files_total, "current": idx, "total": len(chunks),
                        "file_name": uploaded_file.name, "items_count": len(items),
                    })
            except Exception as e:
                errors.append(f"PDF chunk {idx} failed: {repr(e)}")
                if progress_callback:
                    progress_callback({
                        "event": "chunk_failed", "file_current": file_index,
                        "file_total": files_total, "current": idx, "total": len(chunks),
                        "file_name": uploaded_file.name, "error": str(e),
                    })

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
        if progress_callback:
            progress_callback({
                "event": "pdf_completed", "current": file_index, "total": files_total,
                "file_name": uploaded_file.name, "items_count": len(all_items),
            })

    return results

