from __future__ import annotations

import io
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from zipfile import BadZipFile, ZipFile


MAX_PDF_FILES = 20
MAX_JIRA_PDFS = MAX_PDF_FILES
MAX_SINGLE_PDF_BYTES = 50 * 1024 * 1024
MAX_TOTAL_UNPACKED_BYTES = 500 * 1024 * 1024


def _safe_archive_name(name: str) -> PurePosixPath:
    normalized = str(name or "").replace("\\", "/")
    path = PurePosixPath(normalized)
    if not normalized or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Небезопасный путь внутри архива: {name}")
    return path


def _unique_pdf_name(name: str, used_names: set[str]) -> str:
    original = Path(str(name).replace("\\", "/")).name or "document.pdf"
    stem = Path(original).stem[:100] or "document"
    candidate = f"{stem}.pdf"
    index = 2
    while candidate.lower() in used_names:
        candidate = f"{stem}_{index}.pdf"
        index += 1
    used_names.add(candidate.lower())
    return candidate


def _validate_pdf_payload(data: bytes, name: str):
    if len(data) > MAX_SINGLE_PDF_BYTES:
        raise ValueError(f"PDF {name} превышает лимит 50 МБ.")


def _zip_pdfs(data: bytes) -> list[tuple[str, bytes]]:
    try:
        with ZipFile(io.BytesIO(data)) as archive:
            candidates = []
            total_size = 0
            for info in archive.infolist():
                if info.is_dir():
                    continue
                safe_path = _safe_archive_name(info.filename)
                if safe_path.suffix.lower() != ".pdf":
                    continue
                if info.flag_bits & 0x1:
                    raise ValueError(f"PDF {info.filename} зашифрован паролем.")
                total_size += int(info.file_size)
                candidates.append(info)
            if len(candidates) > MAX_JIRA_PDFS:
                raise ValueError(f"В архиве больше {MAX_JIRA_PDFS} PDF-файлов.")
            if total_size > MAX_TOTAL_UNPACKED_BYTES:
                raise ValueError("Распакованный архив превышает лимит 500 МБ.")
            return [(info.filename, archive.read(info)) for info in candidates]
    except BadZipFile as exc:
        raise ValueError("ZIP-архив повреждён или имеет неподдерживаемый формат.") from exc


def _seven_zip_pdfs(data: bytes, work_dir: Path, archive_index: int) -> list[tuple[str, bytes]]:
    try:
        import py7zr
    except ImportError as exc:
        raise ValueError("Для архивов 7z установите зависимость py7zr.") from exc

    extract_dir = work_dir / f"_7z_{archive_index}"
    extract_dir.mkdir(parents=True, exist_ok=True)
    try:
        with py7zr.SevenZipFile(io.BytesIO(data), mode="r") as archive:
            infos = [info for info in archive.list() if not getattr(info, "is_directory", False)]
            candidates = []
            total_size = 0
            for info in infos:
                safe_path = _safe_archive_name(info.filename)
                if safe_path.suffix.lower() != ".pdf":
                    continue
                total_size += int(getattr(info, "uncompressed", 0) or 0)
                candidates.append((info.filename, safe_path))
            if len(candidates) > MAX_JIRA_PDFS:
                raise ValueError(f"В архиве больше {MAX_JIRA_PDFS} PDF-файлов.")
            if total_size > MAX_TOTAL_UNPACKED_BYTES:
                raise ValueError("Распакованный архив превышает лимит 500 МБ.")
            archive.extract(path=extract_dir, targets=[name for name, _ in candidates])

        result = []
        root = extract_dir.resolve()
        for original_name, safe_path in candidates:
            extracted = (extract_dir / Path(*safe_path.parts)).resolve()
            try:
                extracted.relative_to(root)
            except ValueError as exc:
                raise ValueError(f"Небезопасный путь внутри архива: {original_name}") from exc
            result.append((original_name, extracted.read_bytes()))
        return result
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("7z-архив повреждён или имеет неподдерживаемый формат.") from exc
    finally:
        shutil.rmtree(extract_dir, ignore_errors=True)


def stage_pdf_uploads(uploaded_files, prefix: str = "project_brain_pdf_stage_") -> list[dict[str, str]]:
    staged_dir = Path(tempfile.mkdtemp(prefix=prefix))
    used_names: set[str] = set()
    collected: list[tuple[str, bytes]] = []

    try:
        for archive_index, uploaded_file in enumerate(uploaded_files):
            upload_name = uploaded_file.name or "pdf_upload"
            suffix = Path(upload_name).suffix.lower()
            payload = bytes(uploaded_file.getbuffer())
            if suffix == ".pdf":
                collected.append((upload_name, payload))
            elif suffix == ".zip":
                collected.extend(_zip_pdfs(payload))
            elif suffix == ".7z":
                collected.extend(_seven_zip_pdfs(payload, staged_dir, archive_index))
            else:
                raise ValueError(f"Неподдерживаемый тип файла: {suffix or upload_name}")

            if len(collected) > MAX_JIRA_PDFS:
                raise ValueError(f"Можно обработать не более {MAX_JIRA_PDFS} PDF-файлов за один запуск.")

        if not collected:
            raise ValueError("В загрузке не найдено ни одного PDF-файла.")
        if sum(len(payload) for _, payload in collected) > MAX_TOTAL_UNPACKED_BYTES:
            raise ValueError("Общий размер распакованных PDF превышает лимит 500 МБ.")

        specs = []
        for original_name, payload in collected:
            _validate_pdf_payload(payload, original_name)
            safe_name = _unique_pdf_name(original_name, used_names)
            path = staged_dir / safe_name
            path.write_bytes(payload)
            specs.append({"name": safe_name, "path": str(path)})
        return specs
    except Exception:
        shutil.rmtree(staged_dir, ignore_errors=True)
        raise


def stage_jira_uploads(uploaded_files, prefix: str = "project_brain_jira_stage_") -> list[dict[str, str]]:
    """Backward-compatible Jira wrapper around the shared PDF stager."""
    return stage_pdf_uploads(uploaded_files, prefix=prefix)
