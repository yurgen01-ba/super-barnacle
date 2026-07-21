import json
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional

import whisper

from ai.local_meeting_extractor import extract_meeting_knowledge_local
from ai.meeting_extractor import extract_meeting_knowledge
from builders.fact_builder import FactBuilder
from config import WHISPER_MODEL_NAME
from transcription.quality_config import build_whisper_transcribe_kwargs, get_default_language
from transcription.domain_glossary import apply_domain_glossary_repair
from transcription.quality_score import score_transcript_segment
from transcription.segment_retry import should_retry_segment, choose_better_segment
from transcription.context_stitching import build_initial_prompt, update_previous_context
from transcription.meeting_audio_integration import process_audio_with_selected_backend
from extractors.screen import cleanup_frames, deduplicate_similar_frames, extract_video_frames
from providers.vision.factory import create_vision_provider
from utils.text import chunk_text
from utils.video_files import cleanup_file, save_uploaded_file_to_temp


whisper_model = None
ProgressCallback = Callable[[dict], None]


def _get_legacy_whisper_model():
    """Load the fallback model only if WhisperX is unavailable."""
    global whisper_model
    if whisper_model is None:
        whisper_model = whisper.load_model(WHISPER_MODEL_NAME)
    return whisper_model


def _emit(callback: ProgressCallback | None, event: dict):
    if callback:
        try:
            callback(event)
        except Exception:
            pass


def get_video_duration_seconds(video_path: str) -> int:
    command = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", video_path]
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        data = json.loads(result.stdout or "{}")
        return int(float(data.get("format", {}).get("duration", 0)))
    except Exception:
        return 0


def choose_audio_segment_seconds(duration_seconds: int) -> int:
    if duration_seconds <= 0:
        return 20 * 60
    if duration_seconds <= 15 * 60:
        return duration_seconds
    if duration_seconds <= 60 * 60:
        return 15 * 60
    if duration_seconds <= 2 * 60 * 60:
        return 20 * 60
    return 30 * 60


def choose_max_screen_frames(
    duration_seconds: int,
    interval_seconds: int,
    hard_limit: int = 30,
) -> int:
    """Choose one candidate frame per interval, bounded for local inference."""
    if duration_seconds <= 0:
        return 1
    interval = max(int(interval_seconds or 60), 1)
    return max(1, min(hard_limit, (duration_seconds + interval - 1) // interval))


def split_video_to_audio_segments(video_path: str, segment_seconds: int) -> List[str]:
    output_dir = tempfile.mkdtemp(prefix="project_brain_audio_segments_")
    output_pattern = str(Path(output_dir) / "segment_%03d.wav")
    command = [
        "ffmpeg", "-y", "-i", video_path, "-vn",
        "-acodec", "pcm_s16le", "-ar", "16000", "-ac", "1",
        "-f", "segment", "-segment_time", str(max(segment_seconds, 1)), output_pattern,
    ]
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return sorted(str(p) for p in Path(output_dir).glob("segment_*.wav"))




def _quality_to_dict(quality) -> dict:
    return {
        "score": float(getattr(quality, "score", 0.0)),
        "label": str(getattr(quality, "label", "unknown")),
        "reasons": list(getattr(quality, "reasons", []) or []),
    }


def _format_transcript_segment(
    index: int,
    detected_language: str,
    quality,
    text: str,
) -> str:
    quality_dict = _quality_to_dict(quality)
    return (
        f"\n\n[Segment {index} | "
        f"language={detected_language} | "
        f"quality={quality_dict['label']}:{quality_dict['score']}]\n"
        f"{text}"
    )


def transcribe_audio_segments(
    audio_segments: List[str],
    language: Optional[str] = None,
    audio_progress_callback: ProgressCallback | None = None,
) -> dict:
    raw_parts: list[str] = []
    repaired_parts: list[str] = []
    segments: list[dict] = []
    total = len(audio_segments)
    effective_language = get_default_language(language)
    previous_context = ""

    for index, segment_path in enumerate(audio_segments, start=1):
        started_at = time.time()

        _emit(
            audio_progress_callback,
            {
                "event": "audio_segment_started",
                "current": index,
                "total": total,
                "segment_path": str(segment_path),
            },
        )

        initial_prompt = build_initial_prompt(previous_context)
        kwargs = build_whisper_transcribe_kwargs(
            language=effective_language,
            initial_prompt=initial_prompt,
        )

        result = _get_legacy_whisper_model().transcribe(segment_path, **kwargs)

        raw_text = str(result.get("text") or "").strip()
        repaired_text = apply_domain_glossary_repair(raw_text)
        detected_language = str(result.get("language") or effective_language)
        quality = score_transcript_segment(repaired_text, language=effective_language)
        quality_dict = _quality_to_dict(quality)

        segment_record = {
            "index": index,
            "total": total,
            "segment_path": str(segment_path),
            "detected_language": detected_language,
            "raw_text": raw_text,
            "repaired_text": repaired_text,
            "quality": quality_dict,
            "retried": False,
            "elapsed_seconds": round(time.time() - started_at, 1),
        }

        if should_retry_segment(segment_record["quality"]):
            retry_kwargs = build_whisper_transcribe_kwargs(
                language=effective_language,
                initial_prompt=initial_prompt,
                retry=True,
            )
            retry_result = _get_legacy_whisper_model().transcribe(segment_path, **retry_kwargs)

            retry_raw_text = str(retry_result.get("text") or "").strip()
            retry_repaired_text = apply_domain_glossary_repair(retry_raw_text)
            retry_detected_language = str(retry_result.get("language") or effective_language)
            retry_quality = score_transcript_segment(
                retry_repaired_text,
                language=effective_language,
            )

            retry_record = {
                "index": index,
                "total": total,
                "segment_path": str(segment_path),
                "detected_language": retry_detected_language,
                "raw_text": retry_raw_text,
                "repaired_text": retry_repaired_text,
                "quality": _quality_to_dict(retry_quality),
                "retried": True,
                "elapsed_seconds": round(time.time() - started_at, 1),
            }

            segment_record = choose_better_segment(segment_record, retry_record)

            raw_text = segment_record["raw_text"]
            repaired_text = segment_record["repaired_text"]
            detected_language = segment_record["detected_language"]
            quality = score_transcript_segment(repaired_text, language=effective_language)
            segment_record["quality"] = _quality_to_dict(quality)

        if raw_text:
            raw_parts.append(
                _format_transcript_segment(
                    index=index,
                    detected_language=detected_language,
                    quality=quality,
                    text=raw_text,
                )
            )

        if repaired_text:
            repaired_parts.append(
                _format_transcript_segment(
                    index=index,
                    detected_language=detected_language,
                    quality=quality,
                    text=repaired_text,
                )
            )

        segments.append(segment_record)
        previous_context = update_previous_context(previous_context, repaired_text)

        _emit(
            audio_progress_callback,
            {
                "event": "audio_segment_completed",
                "current": index,
                "total": total,
                "detected_language": detected_language,
                "text": repaired_text,
                "transcript": repaired_text,
                "segment_text": repaired_text,
                "raw_text": raw_text,
                "quality_score": segment_record["quality"]["score"],
                "quality_label": segment_record["quality"]["label"],
                "quality_reasons": segment_record["quality"]["reasons"],
                "retried": segment_record["retried"],
                "text_length": len(repaired_text),
                "segment_path": str(segment_path),
                "elapsed_seconds": segment_record["elapsed_seconds"],
            },
        )

    raw_transcript = "\n".join(raw_parts).strip()
    repaired_transcript = "\n".join(repaired_parts).strip()

    quality_scores = [
        float(segment.get("quality", {}).get("score") or 0.0)
        for segment in segments
    ]

    return {
        "raw_transcript": raw_transcript,
        "clean_transcript": repaired_transcript,
        "repaired_transcript": repaired_transcript,
        "segments": segments,
        "quality": {
            "segments": len(segments),
            "bad_segments": len(
                [s for s in segments if s.get("quality", {}).get("label") == "bad"]
            ),
            "medium_segments": len(
                [s for s in segments if s.get("quality", {}).get("label") == "medium"]
            ),
            "good_segments": len(
                [s for s in segments if s.get("quality", {}).get("label") == "good"]
            ),
            "retried_segments": len([s for s in segments if s.get("retried")]),
            "average_score": round(sum(quality_scores) / max(len(quality_scores), 1), 3),
        },
    }


def cleanup_segments(audio_segments: List[str]):
    if not audio_segments:
        return
    parent = Path(audio_segments[0]).parent
    for segment in audio_segments:
        try:
            Path(segment).unlink(missing_ok=True)
        except Exception:
            pass
    try:
        parent.rmdir()
    except OSError:
        pass


def extract_transcript_knowledge(
    chunk: str,
    source: str,
    provider: str = "ollama",
    model: str = "qwen2.5:7b",
    host: str = "http://localhost:11434",
    timeout_seconds: int = 180,
):
    if provider == "ollama":
        return extract_meeting_knowledge_local(chunk, source=source, model=model, host=host, timeout_seconds=timeout_seconds)

    if provider == "claude":
        return extract_meeting_knowledge(chunk, source=source)

    raise ValueError(f"Unsupported transcript extractor provider: {provider}")


def process_meeting_video(
    uploaded_file,
    source: str = None,
    segment_seconds: Optional[int] = None,
    language: Optional[str] = None,
    analyze_screen: bool = False,
    screen_interval_seconds: int = 60,
    max_screen_frames: int | None = None,
    screen_dedup_distance: int = 8,
    vision_provider_name: str = "ollama",
    vision_model: str = "qwen2.5vl:3b",
    vision_host: str = "http://localhost:11434",
    vision_timeout_seconds: int = 60,
    transcript_extractor_provider: str = "ollama",
    transcript_extractor_model: str = "qwen2.5:7b",
    transcript_extractor_host: str = "http://localhost:11434",
    transcript_extractor_timeout_seconds: int = 180,
    extract_canonical_facts: bool = True,
    fact_extractor_model: str = "qwen2.5:7b",
    fact_extractor_host: str = "http://localhost:11434",
    fact_extractor_timeout_seconds: int = 240,
    vision_progress_callback: ProgressCallback | None = None,
    audio_progress_callback: ProgressCallback | None = None,
    fact_progress_callback: ProgressCallback | None = None,
    screen_items_callback: Callable[[list[dict]], None] | None = None,
    use_audio_intelligence: bool = True,
    min_speakers: int | None = 2,
    max_speakers: int | None = 6,
    local_transcript_repair_enabled: bool = True,
    transcript_repair_min_bad_seconds: float = 6.0,
    transcript_repair_min_quality_gain: float = 0.12,
    diarization_correction_enabled: bool = True,
    diarization_min_new_run_words: int = 2,
    diarization_min_new_run_seconds: float = 0.65,
    project_id: str = "default",
) -> Dict:
    video_path = None
    audio_segments = []
    frame_paths = []
    unique_frame_paths = []
    source = source or f"meeting_video:{uploaded_file.name}"

    try:
        _emit(audio_progress_callback, {"event": "video_save_started"})
        video_path = save_uploaded_file_to_temp(uploaded_file)
        duration_seconds = get_video_duration_seconds(video_path)
        if max_screen_frames is None:
            max_screen_frames = choose_max_screen_frames(
                duration_seconds,
                screen_interval_seconds,
            )
        _emit(audio_progress_callback, {"event": "video_ready", "duration_seconds": duration_seconds})

        transcript = ""
        raw_transcript = ""
        clean_transcript = ""
        repaired_transcript = ""
        transcript_quality = {}
        transcript_segments = []
        transcript_items = []
        screen_items = []
        canonical_facts = []
        fact_save_results = []
        errors = []
        chunks = []
        dedup_stats = {}

        if analyze_screen:
            try:
                _emit(vision_progress_callback, {"event": "screen_stage_started", "message": "Extracting video frames before audio transcription", "current": 0, "total": max_screen_frames})
                frame_paths = extract_video_frames(video_path=video_path, interval_seconds=screen_interval_seconds, max_frames=max_screen_frames)
                unique_frame_paths, dedup_stats = deduplicate_similar_frames(frame_paths, max_distance=screen_dedup_distance)
                _emit(vision_progress_callback, {"event": "frames_ready", "current": 0, "total": len(unique_frame_paths), "input_frames": len(frame_paths), "unique_frames": len(unique_frame_paths), "dedup_stats": dedup_stats})

                if unique_frame_paths:
                    vision_provider = create_vision_provider(provider_name=vision_provider_name, model=vision_model, host=vision_host, batch_size=1, timeout_seconds=vision_timeout_seconds)
                    screen_items = vision_provider.analyze_frames(frame_paths=unique_frame_paths, source=f"{source}:screen", progress_callback=vision_progress_callback)

                    if screen_items_callback and screen_items:
                        screen_items_callback(screen_items)

            except Exception as e:
                errors.append(f"Screen analysis failed safely: {repr(e)}")

        _emit(audio_progress_callback, {"event": "audio_stage_started"})

        audio_intelligence_result = None
        if use_audio_intelligence:
            try:
                audio_intelligence_result = process_audio_with_selected_backend(
                    video_path,
                    language,
                    min_speakers,
                    max_speakers,
                    audio_progress_callback,
                    local_transcript_repair_enabled=local_transcript_repair_enabled,
                    transcript_repair_min_bad_seconds=transcript_repair_min_bad_seconds,
                    transcript_repair_min_quality_gain=transcript_repair_min_quality_gain,
                    diarization_correction_enabled=diarization_correction_enabled,
                    diarization_min_new_run_words=diarization_min_new_run_words,
                    diarization_min_new_run_seconds=diarization_min_new_run_seconds,
                )
            except Exception as exc:
                errors.append(f"Audio Intelligence failed; fallback to legacy Whisper: {repr(exc)}")

        if segment_seconds is None:
            segment_seconds = choose_audio_segment_seconds(duration_seconds)

        _emit(audio_progress_callback, {"event": "audio_split_started", "segment_seconds": segment_seconds})
        audio_segments = split_video_to_audio_segments(video_path, segment_seconds=segment_seconds)
        _emit(audio_progress_callback, {"event": "audio_split_completed", "segments_count": len(audio_segments), "segment_seconds": segment_seconds})

        if audio_intelligence_result:
            raw_transcript = audio_intelligence_result.get("text", "")
            clean_transcript = raw_transcript
            repaired_transcript = audio_intelligence_result.get("speaker_transcript") or raw_transcript
            transcript_quality = {"backend": audio_intelligence_result.get("backend"), "warnings": audio_intelligence_result.get("warnings", [])}
            transcript_segments = audio_intelligence_result.get("segments", [])
            transcript = repaired_transcript
        else:
            transcript_bundle = transcribe_audio_segments(audio_segments, language=language, audio_progress_callback=audio_progress_callback)
            raw_transcript = transcript_bundle.get("raw_transcript", "")
            clean_transcript = transcript_bundle.get("clean_transcript", "")
            repaired_transcript = transcript_bundle.get("repaired_transcript", "")
            transcript_quality = transcript_bundle.get("quality", {})
            transcript_segments = transcript_bundle.get("segments", [])
            transcript = repaired_transcript or clean_transcript or raw_transcript

        usable_transcript_segments = [
            segment for segment in transcript_segments
            if segment.get("quality", {}).get("label") != "bad"
        ]
        blocked_transcript_segments = [
            segment for segment in transcript_segments
            if segment.get("quality", {}).get("label") == "bad"
        ]

        extraction_transcript = "\n\n".join(
            segment.get("repaired_text", "")
            for segment in usable_transcript_segments
            if segment.get("repaired_text")
        ).strip() or transcript

        _emit(audio_progress_callback, {
            "event": "transcript_ready",
            "transcript_length": len(transcript or ""),
            "extraction_transcript_length": len(extraction_transcript or ""),
            "blocked_bad_segments": len(blocked_transcript_segments),
            "transcript_quality": transcript_quality,
            "quality": transcript_quality,
        })

        if extraction_transcript:
            chunks = chunk_text(extraction_transcript, max_chars=8000, overlap_chars=800)

            if extract_canonical_facts:
                fact_builder = FactBuilder(
                    model=fact_extractor_model,
                    host=fact_extractor_host,
                    timeout_seconds=fact_extractor_timeout_seconds,
                    project_id=project_id,
                )

                _emit(fact_progress_callback, {"event": "fact_extraction_started", "chunks_count": len(chunks), "model": fact_extractor_model})

                for idx, chunk in enumerate(chunks, start=1):
                    started_at = time.time()
                    fact_source = f"{source}:transcript_chunk_{idx}"

                    _emit(fact_progress_callback, {"event": "fact_chunk_started", "current": idx, "total": len(chunks), "source": fact_source, "model": fact_extractor_model})

                    try:
                        fact_result = fact_builder.build_and_save_facts(text=chunk, source=fact_source, source_type="meeting_transcript")
                        facts = fact_result.get("facts", [])
                        save_result = fact_result.get("save_result", {})
                        canonical_facts.extend(facts)
                        fact_save_results.append(save_result)

                        _emit(fact_progress_callback, {"event": "fact_chunk_completed", "current": idx, "total": len(chunks), "facts_count": len(facts), "saved": save_result.get("saved", 0), "skipped": save_result.get("skipped", 0), "elapsed_seconds": round(time.time() - started_at, 1)})

                    except Exception as e:
                        errors.append(f"Fact extraction chunk {idx} failed: {repr(e)}")
                        _emit(fact_progress_callback, {"event": "fact_chunk_failed", "current": idx, "total": len(chunks), "error": repr(e), "elapsed_seconds": round(time.time() - started_at, 1)})

                _emit(fact_progress_callback, {"event": "fact_extraction_completed", "facts_count": len(canonical_facts), "saved_total": sum(result.get("saved", 0) for result in fact_save_results), "skipped_total": sum(result.get("skipped", 0) for result in fact_save_results)})

            _emit(audio_progress_callback, {"event": "knowledge_extraction_started", "chunks_count": len(chunks), "provider": transcript_extractor_provider, "model": transcript_extractor_model})

            for idx, chunk in enumerate(chunks, start=1):
                started_at = time.time()
                _emit(audio_progress_callback, {"event": "knowledge_chunk_started", "current": idx, "total": len(chunks), "provider": transcript_extractor_provider, "model": transcript_extractor_model})

                try:
                    items = extract_transcript_knowledge(
                        chunk,
                        source=f"{source}:transcript_chunk_{idx}",
                        provider=transcript_extractor_provider,
                        model=transcript_extractor_model,
                        host=transcript_extractor_host,
                        timeout_seconds=transcript_extractor_timeout_seconds,
                    )
                    transcript_items.extend(items)
                    _emit(audio_progress_callback, {"event": "knowledge_chunk_completed", "current": idx, "total": len(chunks), "items_count": len(items), "elapsed_seconds": round(time.time() - started_at, 1)})

                except Exception as e:
                    errors.append(f"Transcript chunk {idx} failed: {repr(e)}")
                    _emit(audio_progress_callback, {"event": "knowledge_chunk_failed", "current": idx, "total": len(chunks), "error": repr(e), "elapsed_seconds": round(time.time() - started_at, 1)})

        all_items = transcript_items + screen_items
        saved_facts_total = sum(result.get("saved", 0) for result in fact_save_results)
        skipped_facts_total = sum(result.get("skipped", 0) for result in fact_save_results)

        warning = None
        if not transcript and not screen_items:
            warning = "No transcript or screen knowledge was extracted from the video."
        elif transcript and not all_items and not canonical_facts:
            warning = "Transcript was created, but no project knowledge or canonical facts were extracted."

        return {
            "file_name": uploaded_file.name,
            "duration_seconds": duration_seconds,
            "audio_segment_seconds": segment_seconds,
            "audio_segments_count": len(audio_segments),
            "transcript": transcript,
            "raw_transcript": raw_transcript,
            "clean_transcript": clean_transcript,
            "repaired_transcript": repaired_transcript,
            "transcript_quality": transcript_quality,
            "transcript_segments": transcript_segments,
            "audio_intelligence": audio_intelligence_result,
            "speaker_transcript": audio_intelligence_result.get("speaker_transcript", "") if audio_intelligence_result else repaired_transcript,
            "word_timestamps": audio_intelligence_result.get("word_timestamps", []) if audio_intelligence_result else [],
            "blocked_transcript_segments": blocked_transcript_segments,
            "extraction_transcript": extraction_transcript,
            "chunks_count": len(chunks),
            "items": all_items,
            "transcript_items": transcript_items,
            "screen_items": screen_items,
            "canonical_facts": canonical_facts,
            "canonical_facts_count": len(canonical_facts),
            "canonical_facts_saved": saved_facts_total,
            "canonical_facts_skipped": skipped_facts_total,
            "screen_frames_count": len(frame_paths),
            "screen_unique_frames_count": len(unique_frame_paths),
            "screen_items_saved_early": bool(screen_items_callback and screen_items),
            "warning": warning,
            "errors": errors,
            "debug": {
                "duration_seconds": duration_seconds,
                "audio_segment_seconds": segment_seconds,
                "audio_segments_count": len(audio_segments),
                "transcript_length": len(transcript or ""),
                "transcript_quality": transcript_quality,
                "blocked_bad_segments": len(blocked_transcript_segments),
                "extraction_transcript_length": len(extraction_transcript or ""),
                "transcript_items_count": len(transcript_items),
                "transcript_extractor_provider": transcript_extractor_provider,
                "transcript_extractor_model": transcript_extractor_model,
                "canonical_facts_count": len(canonical_facts),
                "canonical_facts_saved": saved_facts_total,
                "canonical_facts_skipped": skipped_facts_total,
                "fact_extractor_model": fact_extractor_model,
                "screen_items_count": len(screen_items),
                "screen_items_saved_early": bool(screen_items_callback and screen_items),
                "screen_frames_count": len(frame_paths),
                "screen_unique_frames_count": len(unique_frame_paths),
                "screen_dedup": dedup_stats,
                "vision_model": vision_model,
                "pipeline_order": "screen_first_audio_then_facts_then_knowledge",
            },
        }

    finally:
        cleanup_segments(audio_segments)
        cleanup_frames(frame_paths)
        if video_path:
            cleanup_file(video_path)
