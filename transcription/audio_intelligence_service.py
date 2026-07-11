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
    ) -> dict:
        result = self.transcriber.transcribe(
            audio_path,
            language,
            min_speakers,
            max_speakers,
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
            result.segments
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

        return payload


audio_intelligence_service = (
    AudioIntelligenceService()
)
