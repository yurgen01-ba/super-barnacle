from __future__ import annotations

import json
from typing import Any

from services.artifact_service import artifact_service


def _to_json(value: Any) -> str:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            indent=2,
            default=str,
        )
    except Exception:
        return str(value)


def _artifact(
    extraction_id: str,
    project_id: str,
    artifact_type: str,
    title: str,
    content: Any,
    description: str = "",
    fmt: str = "markdown",
    metadata: dict | None = None,
):
    if content is None:
        return None

    if isinstance(content, (dict, list)):
        content_text = _to_json(content)
        fmt = "json"
    else:
        content_text = str(content)

    if not content_text.strip():
        return None

    return artifact_service.save_artifact(
        extraction_id=extraction_id,
        project_id=project_id,
        artifact_type=artifact_type,
        title=title,
        description=description,
        content=content_text,
        format=fmt,
        metadata=metadata or {},
    )


def _speaker_aware_transcripts(
    result: dict,
) -> tuple[str, str, str, str, list]:
    audio_intelligence = (
        result.get("audio_intelligence")
        or {}
    )

    speaker_transcript = (
        result.get("speaker_transcript")
        or audio_intelligence.get("speaker_transcript")
        or ""
    )

    raw_transcript = (
        result.get("raw_transcript_with_speakers")
        or audio_intelligence.get(
            "raw_transcript_with_speakers"
        )
        or speaker_transcript
        or result.get("raw_transcript")
        or result.get("transcript")
        or ""
    )

    clean_transcript = (
        result.get("clean_transcript_with_speakers")
        or audio_intelligence.get(
            "clean_transcript_with_speakers"
        )
        or speaker_transcript
        or result.get("clean_transcript")
        or ""
    )

    repaired_transcript = (
        result.get("repaired_transcript_with_speakers")
        or audio_intelligence.get(
            "repaired_transcript_with_speakers"
        )
        or speaker_transcript
        or result.get("repaired_transcript")
        or result.get("transcript")
        or ""
    )

    utterances = (
        result.get("speaker_utterances")
        or audio_intelligence.get("speaker_utterances")
        or []
    )

    return (
        raw_transcript,
        clean_transcript,
        repaired_transcript,
        speaker_transcript,
        utterances,
    )


def create_meeting_extraction_artifacts(
    job_result: dict,
    source_name: str = "Meeting extraction",
    project_id: str = "default",
):
    extraction = artifact_service.start_extraction(
        source_id=source_name,
        source_name=source_name,
        source_type="meeting_video",
        project_id=project_id,
    )

    all_transcripts = []
    all_clean_transcripts = []
    all_repaired_transcripts = []
    all_speaker_transcripts = []
    all_screen_items = []
    all_facts = []
    all_debug = []

    result_groups = (
        job_result.get("results", [])
        if isinstance(job_result, dict)
        else []
    )

    for group in result_groups:
        result = (
            group.get("result", group)
            if isinstance(group, dict)
            else {}
        )
        file_name = (
            group.get("file_name")
            or result.get("file_name")
            or source_name
        )

        (
            transcript,
            clean_transcript,
            repaired_transcript,
            speaker_transcript,
            speaker_utterances,
        ) = _speaker_aware_transcripts(result)

        if transcript:
            all_transcripts.append(
                f"# {file_name}\n\n{transcript}"
            )
        if clean_transcript:
            all_clean_transcripts.append(
                f"# {file_name}\n\n{clean_transcript}"
            )
        if repaired_transcript:
            all_repaired_transcripts.append(
                f"# {file_name}\n\n{repaired_transcript}"
            )
        if speaker_transcript:
            all_speaker_transcripts.append(
                f"# {file_name}\n\n{speaker_transcript}"
            )

        if result.get("screen_items"):
            all_screen_items.append(
                {
                    "file_name": file_name,
                    "items": result.get("screen_items"),
                }
            )

        if result.get("canonical_facts"):
            all_facts.append(
                {
                    "file_name": file_name,
                    "facts": result.get("canonical_facts"),
                }
            )

        if result.get("debug"):
            all_debug.append(
                {
                    "file_name": file_name,
                    "debug": result.get("debug"),
                }
            )

        metadata = {
            "file_name": file_name,
            "diarized": bool(speaker_transcript),
            "speaker_count": (
                result.get("audio_intelligence", {})
                .get("runtime", {})
                .get("speaker_count")
            ),
        }

        _artifact(
            extraction.id,
            project_id,
            "transcript",
            f"Raw Transcript — {file_name}",
            transcript,
            (
                "Raw aligned transcript grouped into "
                "speaker utterances when diarization is available."
            ),
            "markdown",
            metadata,
        )

        _artifact(
            extraction.id,
            project_id,
            "clean_transcript",
            f"Clean Transcript — {file_name}",
            clean_transcript,
            (
                "Cleaned transcript with speaker labels "
                "and timestamps."
            ),
            "markdown",
            metadata,
        )

        _artifact(
            extraction.id,
            project_id,
            "repaired_transcript",
            f"Repaired Transcript — {file_name}",
            repaired_transcript,
            (
                "Glossary/repair-enhanced transcript with "
                "speaker labels, used for knowledge extraction."
            ),
            "markdown",
            {
                **metadata,
                "quality": result.get(
                    "transcript_quality"
                ),
            },
        )

        _artifact(
            extraction.id,
            project_id,
            "speaker_transcript",
            f"Speaker Transcript — {file_name}",
            speaker_transcript,
            (
                "Stabilized speaker utterances reconstructed "
                "from word-level diarization."
            ),
            "markdown",
            metadata,
        )

        _artifact(
            extraction.id,
            project_id,
            "speaker_utterances",
            f"Speaker Utterances — {file_name}",
            speaker_utterances,
            (
                "Structured speaker utterances with timestamps, "
                "word counts and confidence."
            ),
            "json",
            metadata,
        )

        _artifact(
            extraction.id,
            project_id,
            "word_timestamps",
            f"Word Timestamps — {file_name}",
            (
                result.get("word_timestamps")
                or result.get(
                    "audio_intelligence",
                    {},
                ).get("word_timestamps")
            ),
            (
                "Word-level timestamps, speaker labels "
                "and alignment scores."
            ),
            "json",
            metadata,
        )

        _artifact(
            extraction.id,
            project_id,
            "audio_intelligence",
            f"Audio Intelligence Runtime — {file_name}",
            result.get("audio_intelligence"),
            (
                "WhisperX backend, model, alignment, "
                "diarization and runtime output."
            ),
            "json",
            metadata,
        )

        _artifact(
            extraction.id,
            project_id,
            "transcript_quality",
            f"Transcript Quality — {file_name}",
            result.get("transcript_quality"),
            "Transcript quality diagnostics.",
            "json",
            metadata,
        )

        _artifact(
            extraction.id,
            project_id,
            "screen_timeline",
            f"Screen Timeline — {file_name}",
            result.get("screen_items"),
            "Screen analysis output.",
            "json",
            metadata,
        )

        _artifact(
            extraction.id,
            project_id,
            "knowledge",
            f"Extracted Knowledge — {file_name}",
            result.get("canonical_facts"),
            "Accepted canonical facts.",
            "json",
            metadata,
        )

        _artifact(
            extraction.id,
            project_id,
            "logs",
            f"Processing Debug — {file_name}",
            result.get("debug"),
            "Processing debug details.",
            "json",
            metadata,
        )

    separator = "\n\n---\n\n"

    _artifact(
        extraction.id,
        project_id,
        "transcript",
        "Merged Raw Transcript",
        separator.join(all_transcripts),
        (
            "Merged speaker-aware raw transcript across "
            "all processed videos."
        ),
        "markdown",
    )

    _artifact(
        extraction.id,
        project_id,
        "clean_transcript",
        "Merged Clean Transcript",
        separator.join(all_clean_transcripts),
        (
            "Merged speaker-aware clean transcript across "
            "all processed videos."
        ),
        "markdown",
    )

    _artifact(
        extraction.id,
        project_id,
        "repaired_transcript",
        "Merged Repaired Transcript",
        separator.join(all_repaired_transcripts),
        (
            "Merged speaker-aware repaired transcript across "
            "all processed videos."
        ),
        "markdown",
    )

    _artifact(
        extraction.id,
        project_id,
        "speaker_transcript",
        "Merged Speaker Transcript",
        separator.join(all_speaker_transcripts),
        (
            "Merged stabilized speaker transcript across "
            "all processed videos."
        ),
        "markdown",
    )

    _artifact(
        extraction.id,
        project_id,
        "screen_timeline",
        "Merged Screen Timeline",
        all_screen_items,
        "Merged screen analysis across videos.",
        "json",
    )

    _artifact(
        extraction.id,
        project_id,
        "knowledge",
        "Merged Extracted Knowledge",
        all_facts,
        "Merged canonical facts across videos.",
        "json",
    )

    _artifact(
        extraction.id,
        project_id,
        "logs",
        "Merged Processing Debug",
        all_debug,
        "Merged processing debug details.",
        "json",
    )

    extraction = artifact_service.complete_extraction(
        extraction,
        statistics={
            "files_count": (
                job_result.get(
                    "files_count",
                    len(result_groups),
                )
                if isinstance(job_result, dict)
                else len(result_groups)
            ),
            "result_groups": len(result_groups),
            "transcript_artifacts": len(all_transcripts),
            "speaker_transcript_artifacts": len(
                all_speaker_transcripts
            ),
            "screen_groups": len(all_screen_items),
            "fact_groups": len(all_facts),
        },
    )

    return extraction


def create_extraction_artifacts_from_job_result(
    job_result: dict,
    job_type: str,
    source_name: str = "Extraction",
    project_id: str = "default",
):
    if job_type == "meeting_video":
        return create_meeting_extraction_artifacts(
            job_result,
            source_name=source_name,
            project_id=project_id,
        )

    extraction = artifact_service.start_extraction(
        source_id=source_name,
        source_name=source_name,
        source_type=job_type,
        project_id=project_id,
    )

    _artifact(
        extraction.id,
        project_id,
        "knowledge",
        "Job Result",
        job_result,
        "Raw extraction result.",
        "json",
        {"job_type": job_type},
    )

    return artifact_service.complete_extraction(
        extraction,
        statistics={"job_type": job_type},
    )
