import unittest
from unittest.mock import patch

from transcription.meeting_audio_integration import (
    merge_audio_intelligence_segments,
    process_audio_segments_with_selected_backend,
)


def _result(text: str, start: float, end: float) -> dict:
    return {
        "text": text,
        "language": "en",
        "backend": "whisperx",
        "model": "large-v3",
        "warnings": [],
        "runtime": {},
        "segments": [{
            "id": 0,
            "start": start,
            "end": end,
            "text": text,
            "speaker": "SPEAKER_00",
            "words": [{"word": text, "start": start, "end": end, "score": 0.9, "speaker": "SPEAKER_00"}],
        }],
        "speaker_utterances": [{
            "speaker": "SPEAKER_00",
            "start": start,
            "end": end,
            "text": text,
            "word_count": 1,
        }],
    }


class MeetingAudioSegmentTests(unittest.TestCase):
    def test_merge_offsets_timestamps_from_later_audio_segments(self):
        merged = merge_audio_intelligence_segments([
            (_result("first", 1, 2), 0),
            (_result("second", 1, 3), 1200),
        ])

        self.assertEqual("first second", merged["text"])
        self.assertEqual(1201.0, merged["segments"][1]["start"])
        self.assertEqual(1203.0, merged["word_timestamps"][1]["end"])
        self.assertIn("00:20:01.000", merged["speaker_transcript"])

    @patch("transcription.meeting_audio_integration.process_audio_with_selected_backend")
    def test_each_audio_segment_is_transcribed_separately(self, transcribe):
        transcribe.side_effect = [_result("first", 0, 1), _result("second", 0, 1)]
        events = []

        result = process_audio_segments_with_selected_backend(
            ["first.wav", "second.wav"],
            segment_seconds=900,
            progress_callback=events.append,
        )

        self.assertEqual(2, transcribe.call_count)
        self.assertEqual(2, result["runtime"]["audio_segments_processed"])
        self.assertEqual(
            ["audio_segment_started", "audio_segment_completed", "audio_segment_started", "audio_segment_completed"],
            [event["event"] for event in events],
        )


if __name__ == "__main__":
    unittest.main()
