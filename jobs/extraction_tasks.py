from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

from extractors.confluence import process_confluence_text
from extractors.jira import process_jira_text
from extractors.jira_pdf import process_jira_pdfs
from extractors.meeting import extract_transcript_knowledge, process_meeting_video
from extractors.slack import process_slack_text
from extractors.files import extract_file_text
from jobs.running_job import RunningJob
from jobs.segment_persistence import make_transcript_segment_callback
from jobs.extraction_artifact_integration import create_meeting_extraction_artifacts
from progress.job_progress import JobProgress
from repositories.memory_repository import MemoryRepository
from repositories.source_repository import SourceRepository
from repositories.workspace_repository import workspace_repository
from services.artifact_service import artifact_service
from services.participant_extraction_service import (
    extract_participants_from_text,
)
from services.speaker_sample_service import create_speaker_samples
from utils.text import chunk_text


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


def _save_items(items: list[dict], default_source: str, project_id: str = "default") -> dict[str, Any]:
    memory_repository = MemoryRepository(project_id=project_id)
    saved, skipped, errors = memory_repository.save_items(items, default_source=default_source)
    return {"saved": saved, "skipped": skipped, "errors": errors, "items_count": len(items)}


def _save_source(name: str, source_type: str, source_ref: str, text: str, project_id: str = "default") -> dict[str, Any]:
    result = SourceRepository().save_document(
        name=name,
        source_type=source_type,
        source_ref=source_ref,
        text=text,
        project_id=project_id,
    )
    workspace_repository.log_event(
        project_id,
        "source",
        f"Добавлен источник: {name}",
        {"source_type": source_type, "source_ref": source_ref, **result},
    )
    return result


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


def _make_meeting_progress_callbacks(progress: JobProgress, file_name: str, file_index: int, files_total: int, source: str, project_id: str = "default"):
    file_base = (file_index - 1) / max(files_total, 1)
    file_span = 1 / max(files_total, 1)
    save_segment_callback = make_transcript_segment_callback(file_name=file_name, source=source, project_id=project_id)

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


def process_slack_text_job(text: str, chunk_size: int = 12, project_id: str = "default", job: RunningJob | None = None) -> dict[str, Any]:
    progress = JobProgress(job) if job else None
    if progress:
        progress.update(0.05, "source", "Saving Slack source document")
    source_save_result = _save_source("Slack paste", "slack", "manual_paste", text, project_id)
    extract_participants_from_text(
        text=text,
        source_type="slack",
        source_ref="manual_paste",
        project_id=project_id,
    )
    if progress:
        progress.update(0.25, "extraction", "Extracting Slack knowledge")
    result = process_slack_text(text, chunk_size=chunk_size)
    if progress:
        progress.update(0.75, "memory", "Saving Slack knowledge")
    save_result = _save_items(result.get("items", []), default_source="slack_paste", project_id=project_id)
    if progress:
        progress.update(1.0, "completed", "Slack extraction completed")
    return {"source": source_save_result, "result": result, "save_result": save_result}


def process_jira_text_job(text: str, project_id: str = "default", job: RunningJob | None = None) -> dict[str, Any]:
    progress = JobProgress(job) if job else None
    if progress:
        progress.update(0.05, "source", "Saving Jira source document")
    source_save_result = _save_source("Jira text paste", "jira_text", "manual_paste", text, project_id)
    extract_participants_from_text(
        text=text,
        source_type="jira",
        source_ref="manual_paste",
        project_id=project_id,
    )
    if progress:
        progress.update(0.25, "extraction", "Extracting Jira knowledge")
    result = process_jira_text(text)
    if progress:
        progress.update(0.75, "memory", "Saving Jira knowledge")
    save_result = _save_items(result.get("items", []), default_source="jira_text", project_id=project_id)
    if progress:
        progress.update(1.0, "completed", "Jira text extraction completed")
    return {"source": source_save_result, "result": result, "save_result": save_result}


def process_confluence_article_job(text: str, title: str = "Confluence article", project_id: str = "default", job: RunningJob | None = None) -> dict[str, Any]:
    progress = JobProgress(job) if job else None
    if progress:
        progress.update(0.05, "source", "Saving Confluence source document")
    source_save_result = _save_source(title, "confluence", title, text, project_id)
    extract_participants_from_text(
        text=text,
        source_type="confluence",
        source_ref=title,
        project_id=project_id,
    )
    if progress:
        progress.update(0.25, "extraction", "Extracting Confluence knowledge")
    result = process_confluence_text(text=text, title=title)
    if progress:
        progress.update(0.75, "memory", "Saving Confluence knowledge")
    save_result = _save_items(result.get("items", []), default_source=f"confluence:{title}", project_id=project_id)
    if progress:
        progress.update(1.0, "completed", "Confluence extraction completed")
    return {"source": source_save_result, "result": result, "save_result": save_result}


def process_jira_pdfs_job(file_specs: list[dict[str, str]], project_id: str = "default", job: RunningJob | None = None) -> dict[str, Any]:
    progress = JobProgress(job) if job else None
    pdf_files = [StagedPdfFile(path=spec["path"], name=spec["name"]) for spec in file_specs]
    if progress:
        progress.update(0.05, "extraction", f"Processing {len(pdf_files)} Jira PDF file(s)")
    results = process_jira_pdfs(pdf_files)
    saved_results = []
    for index, result in enumerate(results, start=1):
        if progress:
            progress.update(min(0.15 + index / max(len(results), 1) * 0.7, 0.85), "memory", f"Saving Jira PDF knowledge: {result.get('file_name')}")
        source_save_result = _save_source(result["file_name"], "jira_pdf", result["file_name"], result.get("text", ""), project_id)
        extract_participants_from_text(
            text=result.get("text", ""),
            source_type="jira",
            source_ref=result["file_name"],
            project_id=project_id,
        )
        save_result = _save_items(result.get("items", []), default_source=f"jira_pdf:{result['file_name']}", project_id=project_id)
        saved_results.append({"source": source_save_result, "result": result, "save_result": save_result})
    if progress:
        progress.update(1.0, "completed", "Jira PDF extraction completed")
    return {"files_count": len(file_specs), "results": saved_results}


def process_files_job(
    file_specs: list[dict[str, str]],
    project_id: str = "default",
    job: RunningJob | None = None,
) -> dict[str, Any]:
    progress = JobProgress(job) if job else None
    results = []
    extraction = artifact_service.start_extraction(
        source_id=",".join(spec["name"] for spec in file_specs),
        source_name=", ".join(spec["name"] for spec in file_specs),
        source_type="uploaded_files",
        project_id=project_id,
    )
    total = max(len(file_specs), 1)
    settings = workspace_repository.get_settings(project_id)

    for index, spec in enumerate(file_specs, start=1):
        if progress:
            progress.update(
                (index - 1) / total,
                "files:extract",
                f"Reading file {index}/{total}: {spec['name']}",
            )
        try:
            text = extract_file_text(spec["path"])
            if not text.strip():
                raise ValueError("No readable text found")
            source_result = _save_source(
                spec["name"],
                f"file:{Path(spec['name']).suffix.lower().lstrip('.')}",
                spec["name"],
                text,
                project_id,
            )
            chunks = chunk_text(text, max_chars=8000, overlap_chars=500)
            knowledge_items = []
            knowledge_errors = []
            for chunk_index, chunk in enumerate(chunks, start=1):
                try:
                    knowledge_items.extend(extract_transcript_knowledge(
                        chunk,
                        source=f"file:{spec['name']}:chunk_{chunk_index}",
                        provider=settings.get("transcript_extractor_provider", "ollama"),
                        model=settings.get("transcript_extractor_model", "qwen2.5:7b"),
                        host=settings.get("transcript_extractor_host", "http://localhost:11434"),
                        timeout_seconds=int(settings.get("transcript_extractor_timeout_seconds", 180)),
                    ))
                except Exception as exc:
                    knowledge_errors.append(
                        f"Chunk {chunk_index}: {type(exc).__name__}: {exc}"
                    )
            knowledge = {
                "title": spec["name"],
                "chunks_count": len(chunks),
                "items": knowledge_items,
                "errors": knowledge_errors,
            }
            save_result = _save_items(
                knowledge.get("items", []),
                default_source=f"file:{spec['name']}",
                project_id=project_id,
            )
            artifact_service.save_artifact(
                extraction_id=extraction.id,
                project_id=project_id,
                artifact_type="source_text",
                title=f"Извлечённый текст — {spec['name']}",
                content=text,
                description="Текст, извлечённый из загруженного файла.",
                format="markdown" if Path(spec["name"]).suffix.lower() == ".md" else "text",
                metadata={"file_name": spec["name"], "source": source_result},
            )
            artifact_service.save_artifact(
                extraction_id=extraction.id,
                project_id=project_id,
                artifact_type="knowledge",
                title=f"Извлечённые знания — {spec['name']}",
                content=json.dumps(knowledge, ensure_ascii=False, indent=2, default=str),
                description="Структурированные знания, полученные из файла.",
                format="json",
                metadata={"file_name": spec["name"], "save_result": save_result},
            )
            results.append({
                "file_name": spec["name"],
                "status": "completed",
                "text_length": len(text),
                "knowledge_items": len(knowledge.get("items", [])),
                "errors": knowledge.get("errors", []),
            })
        except Exception as exc:
            results.append({
                "file_name": spec["name"],
                "status": "failed",
                "error": f"{type(exc).__name__}: {exc}",
            })

    extraction = artifact_service.complete_extraction(
        extraction,
        statistics={
            "files": len(file_specs),
            "completed": sum(item["status"] == "completed" for item in results),
            "failed": sum(item["status"] == "failed" for item in results),
        },
    )
    workspace_repository.log_event(
        project_id,
        "artifact",
        "Обработаны загруженные файлы",
        {
            "extraction_id": extraction.id,
            "results": results,
            "logs": list(job.logs) if job else [],
        },
    )
    if progress:
        progress.update(1.0, "completed", "File processing completed. Artifacts are ready.")
    return {
        "files_count": len(file_specs),
        "results": results,
        "extraction": extraction.to_dict(),
    }


def process_meeting_videos_job(file_specs: list[dict[str, str]], settings: dict[str, Any], project_id: str = "default", job: RunningJob | None = None) -> dict[str, Any]:
    progress = JobProgress(job) if job else None
    results = []
    total = max(len(file_specs), 1)

    for index, spec in enumerate(file_specs, start=1):
        source = f"meeting_video:{spec['name']}"
        if progress:
            progress.update((index - 1) / total, "meeting", f"Processing meeting video {index}/{total}: {spec['name']}")

        uploaded_file = StagedUploadedFile(path=spec["path"], name=spec["name"])
        runtime_settings = dict(settings)
        runtime_settings.pop("participant_names", None)

        if progress:
            audio_callback, vision_callback, fact_callback = _make_meeting_progress_callbacks(
                progress=progress,
                file_name=spec["name"],
                file_index=index,
                files_total=total,
                source=source,
                project_id=project_id,
            )
            runtime_settings["audio_progress_callback"] = audio_callback
            runtime_settings["vision_progress_callback"] = vision_callback
            runtime_settings["fact_progress_callback"] = fact_callback

        result = process_meeting_video(
            uploaded_file,
            source=source,
            project_id=project_id,
            **runtime_settings,
        )
        speaker_samples = create_speaker_samples(
            spec["path"],
            result,
            project_id=project_id,
            job_id=job.id if job else "manual",
            file_name=spec["name"],
        )

        if progress:
            progress.update(_progress_between((index - 1) / total, 1 / total, 0.90), "meeting:saving", f"{spec['name']}: saving full transcript and extracted knowledge")

        source_save_result = _save_source(spec["name"], "meeting_video_transcript", spec["name"], result.get("transcript", ""), project_id)
        transcript_save_result = _save_items(result.get("transcript_items", []), default_source=source, project_id=project_id)

        screen_save_result = None
        if result.get("screen_items"):
            screen_save_result = _save_items(result.get("screen_items", []), default_source=f"meeting_video_screen:{spec['name']}", project_id=project_id)

        results.append({
            "file_name": spec["name"],
            "source": source_save_result,
            "result": result,
            "transcript_save_result": transcript_save_result,
            "screen_save_result": screen_save_result,
            "speaker_samples": speaker_samples,
        })

        if progress:
            progress.update(index / total, "meeting:completed", f"Meeting video completed {index}/{total}: {spec['name']}")

    job_result = {"files_count": len(file_specs), "results": results}

    extraction = create_meeting_extraction_artifacts(
        job_result,
        source_name=", ".join(spec["name"] for spec in file_specs),
        project_id=project_id,
    )
    job_result["extraction"] = extraction.to_dict()
    workspace_repository.log_event(
        project_id,
        "artifact",
        "Созданы артефакты расшифровки",
        {
            "extraction_id": extraction.id,
            "job_id": job.id if job else None,
            "files": [spec["name"] for spec in file_specs],
            "artifact_count": extraction.artifact_count,
            "logs": list(job.logs) if job else [],
        },
    )

    if progress:
        progress.update(1.0, "completed", "Meeting extraction completed. Artifacts are ready.")

    return job_result
