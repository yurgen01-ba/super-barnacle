from __future__ import annotations

from transcription.audio_transcriber_factory import (
    create_audio_transcriber,
)
from transcription.speaker_utterance_stabilizer import (
    render_speaker_utterances,
    serialize_utterances,
    stabilize_speaker_utterances_with_debug,
    transform_utterances,
)
from transcription.local_segment_repair import repair_transcript_segments


def _clean_text(text: str) -> str:
    try:
        from transcription.clean_transcript_pipeline import (
            clean_transcript_text,
        )
        return clean_transcript_text(text)
    except Exception:
        return text


class AudioIntelligenceService:
    def __init__(self):
        self._transcriber = None

    @property
    def transcriber(self):
        if self._transcriber is None:
            self._transcriber = (
                create_audio_transcriber()
            )
        return self._transcriber

    def reset_backend(self):
        self._transcriber = None

    def process(
        self,
        audio_path: str,
        language: str | None = None,
        min_speakers: int | None = None,
        max_speakers: int | None = None,
        local_transcript_repair_enabled: bool = True,
        transcript_repair_min_bad_seconds: float = 6.0,
        transcript_repair_min_quality_gain: float = 0.12,
        diarization_correction_enabled: bool = True,
        diarization_min_new_run_words: int = 2,
        diarization_min_new_run_seconds: float = 0.65,
    ) -> dict:
        result = self.transcriber.transcribe(
            audio_path,
            language,
            min_speakers,
            max_speakers,
        )
        repair_debug = []
        if local_transcript_repair_enabled and result.segments:
            result.segments, repair_debug = repair_transcript_segments(
                audio_path=audio_path,
                segments=result.segments,
                language=language or result.language or "ru",
                min_bad_seconds=transcript_repair_min_bad_seconds,
                min_quality_gain=transcript_repair_min_quality_gain,
                retranscribe=lambda clip_path: self.transcriber.transcribe(
                    clip_path, language, min_speakers, max_speakers
                ),
            )
            result.text = " ".join(
                segment.text.strip() for segment in result.segments if segment.text.strip()
            )

        payload = result.to_dict()

        startup_warning = getattr(
            self.transcriber,
            "startup_warning",
            None,
        )
        if startup_warning:
            payload.setdefault(
                "warnings",
                [],
            ).append(
                startup_warning
            )

        (
            utterances,
            boundary_debug,
        ) = stabilize_speaker_utterances_with_debug(
            result.segments,
            min_new_run_words=(diarization_min_new_run_words if diarization_correction_enabled else 1),
            min_new_run_duration_seconds=(
                diarization_min_new_run_seconds if diarization_correction_enabled else 0.0
            ),
        )

        clean_utterances = transform_utterances(
            utterances,
            _clean_text,
        )

        raw_speaker_transcript = (
            render_speaker_utterances(
                utterances
            )
        )
        clean_speaker_transcript = (
            render_speaker_utterances(
                clean_utterances
            )
        )

        payload["speaker_utterances"] = (
            serialize_utterances(
                utterances
            )
        )
        payload["speaker_transcript"] = (
            clean_speaker_transcript
            or raw_speaker_transcript
        )
        payload[
            "raw_transcript_with_speakers"
        ] = raw_speaker_transcript
        payload[
            "clean_transcript_with_speakers"
        ] = clean_speaker_transcript
        payload[
            "repaired_transcript_with_speakers"
        ] = clean_speaker_transcript

        payload["word_timestamps"] = [
            {
                "word": word.word,
                "start": word.start,
                "end": word.end,
                "speaker": word.speaker,
                "score": word.score,
            }
            for segment in result.segments
            for word in segment.words
        ]

        runtime = payload.setdefault(
            "runtime",
            {},
        )
        runtime[
            "speaker_utterance_count"
        ] = len(utterances)
        runtime[
            "speaker_transcript_stabilized"
        ] = bool(utterances)
        runtime[
            "speaker_boundary_validation"
        ] = boundary_debug
        runtime["local_transcript_repair_enabled"] = local_transcript_repair_enabled
        runtime["local_transcript_repair"] = repair_debug
        runtime["local_transcript_repairs_accepted"] = sum(
            1 for event in repair_debug if event.get("accepted")
        )
        runtime["diarization_correction_enabled"] = diarization_correction_enabled

        return payload


audio_intelligence_service = (
    AudioIntelligenceService()
)
