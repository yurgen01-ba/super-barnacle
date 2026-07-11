from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

from extractors.confluence import process_confluence_text
from extractors.jira import process_jira_text
from extractors.jira_pdf import process_jira_pdfs
from extractors.meeting import process_meeting_video
from extractors.slack import process_slack_text
from jobs.running_job import RunningJob
from jobs.segment_persistence import make_transcript_segment_callback
from jobs.extraction_artifact_integration import create_meeting_extraction_artifacts
from progress.job_progress import JobProgress
from repositories.memory_repository import MemoryRepository
from repositories.source_repository import SourceRepository


class StagedUploadedFile:
    def __init__(self, path: str, name: str):
        self.path = path
        self.name = name

    def getbuffer(self):
        return Path(self.path).read_bytes()

    def read(self, *args, **kwargs):
        return Path(self.path).read_bytes()


class StagedPdfFile(BytesIO):
    def __init__(self, path: str, name: str):
        self.path = path
        self.name = name
        super().__init__(Path(path).read_bytes())


def _save_items(items: list[dict], default_source: str) -> dict[str, Any]:
    memory_repository = MemoryRepository()
    saved, skipped, errors = memory_repository.save_items(items, default_source=default_source)
    return {"saved": saved, "skipped": skipped, "errors": errors, "items_count": len(items)}


def _save_source(name: str, source_type: str, source_ref: str, text: str) -> dict[str, Any]:
    return SourceRepository().save_document(name=name, source_type=source_type, source_ref=source_ref, text=text)


def _progress_between(base: float, span: float, local_progress: float) -> float:
    return max(0.0, min(0.99, base + span * max(0.0, min(1.0, local_progress))))


def _event_text(event: dict, default: str) -> str:
    current = event.get("current")
    total = event.get("total")
    message = event.get("message")
    if message:
        return str(message)
    if current is not None and total:
        return f"{default} {current}/{total}"
    return default


def _make_meeting_progress_callbacks(progress: JobProgress, file_name: str, file_index: int, files_total: int, source: str):
    file_base = (file_index - 1) / max(files_total, 1)
    file_span = 1 / max(files_total, 1)
    save_segment_callback = make_transcript_segment_callback(file_name=file_name, source=source)

    def update(local_progress: float, stage: str, message: str):
        progress.update(
            _progress_between(file_base, file_span, local_progress),
            stage,
            f"{file_name}: {message}",
        )

    def audio_callback(event: dict):
        name = event.get("event")

        if name == "audio_segment_completed":
            save_result = save_segment_callback(event)
            current = int(event.get("current", 1))
            total = max(int(event.get("total", 1)), 1)
            saved_suffix = "saved to DB" if save_result and save_result.get("saved") else "completed"
            update(0.14 + 0.26 * (current / total), "meeting:transcription", f"Completed audio segment {current}/{total}, {saved_suffix}")
            return

        if name == "video_save_started":
            update(0.02, "meeting:prepare", "Saving uploaded video")
        elif name == "video_ready":
            duration = event.get("duration_seconds", 0)
            update(0.05, "meeting:prepare", f"Video ready, duration {duration}s")
        elif name == "audio_stage_started":
            update(0.08, "meeting:audio", "Starting audio stage")
        elif name == "audio_split_started":
            update(0.10, "meeting:audio", "Splitting video into audio segments")
        elif name == "audio_split_completed":
            count = event.get("segments_count", 0)
            update(0.14, "meeting:audio", f"Audio split completed, segments: {count}")
        elif name == "audio_segment_started":
            current = int(event.get("current", 1))
            total = max(int(event.get("total", 1)), 1)
            update(0.14 + 0.26 * ((current - 1) / total), "meeting:transcription", f"Transcribing audio segment {current}/{total}")
        elif name == "transcript_ready":
            length = event.get("transcript_length", 0)
            update(0.45, "meeting:transcript", f"Transcript ready, length: {length}")
        elif name == "knowledge_extraction_started":
            chunks = event.get("chunks_count", 0)
            update(0.70, "meeting:knowledge", f"Starting transcript knowledge extraction, chunks: {chunks}")
        elif name == "knowledge_chunk_started":
            current = int(event.get("current", 1))
            total = max(int(event.get("total", 1)), 1)
            update(0.70 + 0.18 * ((current - 1) / total), "meeting:knowledge", f"Extracting knowledge chunk {current}/{total}")
        elif name == "knowledge_chunk_completed":
            current = int(event.get("current", 1))
            total = max(int(event.get("total", 1)), 1)
            items = event.get("items_count", 0)
            update(0.70 + 0.18 * (current / total), "meeting:knowledge", f"Knowledge chunk {current}/{total} completed, items: {items}")
        elif name == "knowledge_chunk_failed":
            update(0.88, "meeting:knowledge", f"Knowledge chunk failed: {event.get('error')}")
        else:
            update(0.20, "meeting:audio", _event_text(event, "Audio processing"))

    def vision_callback(event: dict):
        name = event.get("event")
        if name == "screen_stage_started":
            update(0.06, "meeting:vision", "Starting screen analysis")
        elif name == "frames_ready":
            total = event.get("total", 0)
            update(0.10, "meeting:vision", f"Screen frames ready: {total}")
        elif "current" in event and "total" in event:
            current = int(event.get("current", 1))
            total = max(int(event.get("total", 1)), 1)
            update(0.10 + 0.10 * (current / total), "meeting:vision", f"Analyzing screen frame {current}/{total}")
        else:
            update(0.10, "meeting:vision", _event_text(event, "Screen analysis"))

    def fact_callback(event: dict):
        name = event.get("event")
        if name == "fact_extraction_started":
            chunks = event.get("chunks_count", 0)
            update(0.45, "meeting:facts", f"Starting canonical fact extraction, chunks: {chunks}")
        elif name == "fact_chunk_started":
            current = int(event.get("current", 1))
            total = max(int(event.get("total", 1)), 1)
            update(0.45 + 0.20 * ((current - 1) / total), "meeting:facts", f"Extracting facts from chunk {current}/{total}")
        elif name == "fact_chunk_completed":
            current = int(event.get("current", 1))
            total = max(int(event.get("total", 1)), 1)
            facts = event.get("facts_count", 0)
            update(0.45 + 0.20 * (current / total), "meeting:facts", f"Fact chunk {current}/{total} completed, facts: {facts}")
        elif name == "fact_chunk_failed":
            update(0.65, "meeting:facts", f"Fact chunk failed: {event.get('error')}")
        elif name == "fact_extraction_completed":
            facts = event.get("facts_count", 0)
            update(0.70, "meeting:facts", f"Fact extraction completed, facts: {facts}")
        else:
            update(0.55, "meeting:facts", _event_text(event, "Fact extraction"))

    return audio_callback, vision_callback, fact_callback


def process_slack_text_job(text: str, chunk_size: int = 12, job: RunningJob | None = None) -> dict[str, Any]:
    progress = JobProgress(job) if job else None
    if progress:
        progress.update(0.05, "source", "Saving Slack source document")
    source_save_result = _save_source("Slack paste", "slack", "manual_paste", text)
    if progress:
        progress.update(0.25, "extraction", "Extracting Slack knowledge")
    result = process_slack_text(text, chunk_size=chunk_size)
    if progress:
        progress.update(0.75, "memory", "Saving Slack knowledge")
    save_result = _save_items(result.get("items", []), default_source="slack_paste")
    if progress:
        progress.update(1.0, "completed", "Slack extraction completed")
    return {"source": source_save_result, "result": result, "save_result": save_result}


def process_jira_text_job(text: str, job: RunningJob | None = None) -> dict[str, Any]:
    progress = JobProgress(job) if job else None
    if progress:
        progress.update(0.05, "source", "Saving Jira source document")
    source_save_result = _save_source("Jira text paste", "jira_text", "manual_paste", text)
    if progress:
        progress.update(0.25, "extraction", "Extracting Jira knowledge")
    result = process_jira_text(text)
    if progress:
        progress.update(0.75, "memory", "Saving Jira knowledge")
    save_result = _save_items(result.get("items", []), default_source="jira_text")
    if progress:
        progress.update(1.0, "completed", "Jira text extraction completed")
    return {"source": source_save_result, "result": result, "save_result": save_result}


def process_confluence_article_job(text: str, title: str = "Confluence article", job: RunningJob | None = None) -> dict[str, Any]:
    progress = JobProgress(job) if job else None
    if progress:
        progress.update(0.05, "source", "Saving Confluence source document")
    source_save_result = _save_source(title, "confluence", title, text)
    if progress:
        progress.update(0.25, "extraction", "Extracting Confluence knowledge")
    result = process_confluence_text(text=text, title=title)
    if progress:
        progress.update(0.75, "memory", "Saving Confluence knowledge")
    save_result = _save_items(result.get("items", []), default_source=f"confluence:{title}")
    if progress:
        progress.update(1.0, "completed", "Confluence extraction completed")
    return {"source": source_save_result, "result": result, "save_result": save_result}


def process_jira_pdfs_job(file_specs: list[dict[str, str]], job: RunningJob | None = None) -> dict[str, Any]:
    progress = JobProgress(job) if job else None
    pdf_files = [StagedPdfFile(path=spec["path"], name=spec["name"]) for spec in file_specs]
    if progress:
        progress.update(0.05, "extraction", f"Processing {len(pdf_files)} Jira PDF file(s)")
    results = process_jira_pdfs(pdf_files)
    saved_results = []
    for index, result in enumerate(results, start=1):
        if progress:
            progress.update(min(0.15 + index / max(len(results), 1) * 0.7, 0.85), "memory", f"Saving Jira PDF knowledge: {result.get('file_name')}")
        source_save_result = _save_source(result["file_name"], "jira_pdf", result["file_name"], result.get("text", ""))
        save_result = _save_items(result.get("items", []), default_source=f"jira_pdf:{result['file_name']}")
        saved_results.append({"source": source_save_result, "result": result, "save_result": save_result})
    if progress:
        progress.update(1.0, "completed", "Jira PDF extraction completed")
    return {"files_count": len(file_specs), "results": saved_results}


def process_meeting_videos_job(file_specs: list[dict[str, str]], settings: dict[str, Any], job: RunningJob | None = None) -> dict[str, Any]:
    progress = JobProgress(job) if job else None
    results = []
    total = max(len(file_specs), 1)

    for index, spec in enumerate(file_specs, start=1):
        source = f"meeting_video:{spec['name']}"
        if progress:
            progress.update((index - 1) / total, "meeting", f"Processing meeting video {index}/{total}: {spec['name']}")

        uploaded_file = StagedUploadedFile(path=spec["path"], name=spec["name"])
        runtime_settings = dict(settings)

        if progress:
            audio_callback, vision_callback, fact_callback = _make_meeting_progress_callbacks(
                progress=progress,
                file_name=spec["name"],
                file_index=index,
                files_total=total,
                source=source,
            )
            runtime_settings["audio_progress_callback"] = audio_callback
            runtime_settings["vision_progress_callback"] = vision_callback
            runtime_settings["fact_progress_callback"] = fact_callback

        result = process_meeting_video(uploaded_file, source=source, **runtime_settings)

        if progress:
            progress.update(_progress_between((index - 1) / total, 1 / total, 0.90), "meeting:saving", f"{spec['name']}: saving full transcript and extracted knowledge")

        source_save_result = _save_source(spec["name"], "meeting_video_transcript", spec["name"], result.get("transcript", ""))
        transcript_save_result = _save_items(result.get("transcript_items", []), default_source=source)

        screen_save_result = None
        if result.get("screen_items"):
            screen_save_result = _save_items(result.get("screen_items", []), default_source=f"meeting_video_screen:{spec['name']}")

        results.append({
            "file_name": spec["name"],
            "source": source_save_result,
            "result": result,
            "transcript_save_result": transcript_save_result,
            "screen_save_result": screen_save_result,
        })

        if progress:
            progress.update(index / total, "meeting:completed", f"Meeting video completed {index}/{total}: {spec['name']}")

    job_result = {"files_count": len(file_specs), "results": results}

    extraction = create_meeting_extraction_artifacts(
        job_result,
        source_name=", ".join(spec["name"] for spec in file_specs),
        project_id="default",
    )
    job_result["extraction"] = extraction.to_dict()

    if progress:
        progress.update(1.0, "completed", "Meeting extraction completed. Artifacts are ready.")

    return job_result
