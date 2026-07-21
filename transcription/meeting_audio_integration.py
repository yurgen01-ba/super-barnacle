from __future__ import annotations
import time
from transcription.audio_intelligence_service import audio_intelligence_service

def process_audio_with_selected_backend(
    audio_path: str,
    language: str | None = None,
    min_speakers: int | None = 2,
    max_speakers: int | None = 6,
    progress_callback=None,
    **processing_options,
) -> dict:
    if progress_callback: progress_callback({"event":"audio_intelligence_started","language":language})
    result=audio_intelligence_service.process(
        audio_path, language, min_speakers, max_speakers, **processing_options
    )
    if progress_callback: progress_callback({"event":"audio_intelligence_completed","backend":result.get("backend"),"model":result.get("model"),"segments":len(result.get("segments") or []),"warnings":result.get("warnings") or [],"runtime":result.get("runtime") or {}})
    return result


def _shift(value, offset: float):
    return None if value is None else round(float(value) + offset, 3)


def _format_timestamp(seconds: float) -> str:
    minutes, remaining = divmod(max(float(seconds or 0), 0.0), 60)
    hours, minutes = divmod(int(minutes), 60)
    return f"{hours:02d}:{minutes:02d}:{remaining:06.3f}"


def _render_speaker_utterances(utterances: list[dict]) -> str:
    return "\n\n".join(
        f"[{_format_timestamp(item.get('start', 0))}–{_format_timestamp(item.get('end', 0))}] "
        f"{item.get('speaker') or 'SPEAKER_UNKNOWN'}:\n{item.get('text', '')}"
        for item in utterances
        if item.get("text")
    ).strip()


def merge_audio_intelligence_segments(segment_results: list[tuple[dict, float]]) -> dict:
    merged_segments: list[dict] = []
    merged_utterances: list[dict] = []
    warnings: list[str] = []
    texts: list[str] = []
    runtimes: list[dict] = []
    languages: list[str] = []
    backend = ""
    model = ""

    for segment_number, (result, offset) in enumerate(segment_results, start=1):
        text = str(result.get("text") or "").strip()
        if text:
            texts.append(text)
        language = str(result.get("language") or "").strip()
        if language and language != "unknown":
            languages.append(language)
        backend = backend or str(result.get("backend") or "")
        model = model or str(result.get("model") or "")
        runtimes.append(dict(result.get("runtime") or {}))
        warnings.extend(
            f"Segment {segment_number}: {warning}"
            for warning in (result.get("warnings") or [])
        )

        for raw_segment in result.get("segments") or []:
            item = dict(raw_segment)
            item["id"] = len(merged_segments)
            item["start"] = _shift(item.get("start"), offset)
            item["end"] = _shift(item.get("end"), offset)
            words = []
            for raw_word in item.get("words") or []:
                word = dict(raw_word)
                word["start"] = _shift(word.get("start"), offset)
                word["end"] = _shift(word.get("end"), offset)
                words.append(word)
            item["words"] = words
            merged_segments.append(item)

        for raw_utterance in result.get("speaker_utterances") or []:
            utterance = dict(raw_utterance)
            utterance["start"] = _shift(utterance.get("start"), offset)
            utterance["end"] = _shift(utterance.get("end"), offset)
            merged_utterances.append(utterance)

    word_timestamps = [
        {
            "word": word.get("word"),
            "start": word.get("start"),
            "end": word.get("end"),
            "score": word.get("score"),
            "speaker": word.get("speaker") or segment.get("speaker"),
        }
        for segment in merged_segments
        for word in segment.get("words") or []
    ]
    speaker_transcript = _render_speaker_utterances(merged_utterances)
    text = " ".join(texts).strip()
    return {
        "text": text,
        "language": languages[0] if languages else "unknown",
        "backend": backend,
        "model": model,
        "segments": merged_segments,
        "warnings": warnings,
        "runtime": {
            "audio_segments_processed": len(segment_results),
            "segment_runtimes": runtimes,
        },
        "speaker_utterances": merged_utterances,
        "speaker_transcript": speaker_transcript or text,
        "raw_transcript_with_speakers": speaker_transcript,
        "clean_transcript_with_speakers": speaker_transcript,
        "repaired_transcript_with_speakers": speaker_transcript,
        "word_timestamps": word_timestamps,
    }


def process_audio_segments_with_selected_backend(
    audio_segments: list[str],
    segment_seconds: int,
    language: str | None = None,
    min_speakers: int | None = 2,
    max_speakers: int | None = 6,
    progress_callback=None,
    **processing_options,
) -> dict:
    results: list[tuple[dict, float]] = []
    total = len(audio_segments)

    for index, segment_path in enumerate(audio_segments, start=1):
        started_at = time.time()
        if progress_callback:
            progress_callback({
                "event": "audio_segment_started",
                "current": index,
                "total": total,
                "segment_path": segment_path,
            })
        result = process_audio_with_selected_backend(
            segment_path,
            language,
            min_speakers,
            max_speakers,
            None,
            **processing_options,
        )
        offset = float((index - 1) * segment_seconds)
        results.append((result, offset))
        if progress_callback:
            progress_callback({
                "event": "audio_segment_completed",
                "current": index,
                "total": total,
                "segment_path": segment_path,
                "text": result.get("speaker_transcript") or result.get("text") or "",
                "raw_text": result.get("text") or "",
                "detected_language": result.get("language") or language or "unknown",
                "elapsed_seconds": round(time.time() - started_at, 1),
            })

    return merge_audio_intelligence_segments(results)
