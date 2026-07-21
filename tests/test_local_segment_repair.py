import unittest

from transcription.audio_contracts import AudioTranscriptionResult, TranscriptSegment
from transcription.local_segment_repair import find_repair_windows, repair_transcript_segments


def segment(index, start, end, text, speaker="SPEAKER_00"):
    return TranscriptSegment(index, start, end, text, speaker=speaker)


class LocalSegmentRepairTests(unittest.TestCase):
    def test_short_filler_is_not_a_repair_window(self):
        segments = [segment(0, 0.0, 8.0, "well yes")]
        self.assertEqual(find_repair_windows(segments, "en", min_bad_seconds=6.0), [])

    def test_long_corrupted_window_is_detected(self):
        segments = [segment(0, 4.0, 12.0, "ajblue ajblue ajblue ajblue ajblue ajblue")]
        windows = find_repair_windows(segments, "en", min_bad_seconds=6.0)
        self.assertEqual(len(windows), 1)
        self.assertEqual((windows[0].start, windows[0].end), (4.0, 12.0))

    def test_retry_replaces_only_when_quality_improves(self):
        original = [segment(0, 4.0, 12.0, "ajblue ajblue ajblue ajblue ajblue ajblue")]
        retry_result = AudioTranscriptionResult(
            text="We selected a stable payment service because it reduces settlement risk.",
            language="en",
            segments=[
                segment(
                    0,
                    0.0,
                    8.0,
                    "We selected a stable payment service because it reduces settlement risk.",
                )
            ],
            backend="test",
            model="test",
            runtime={},
        )

        repaired, debug = repair_transcript_segments(
            "unused.wav",
            original,
            retranscribe=lambda _: retry_result,
            language="en",
            min_bad_seconds=6.0,
            min_quality_gain=0.05,
            clip_extractor=lambda *_: None,
        )

        self.assertTrue(debug[0]["accepted"])
        self.assertIn("stable payment service", repaired[0].text)
        self.assertEqual((repaired[0].start, repaired[0].end), (4.0, 12.0))
        self.assertEqual(repaired[0].speaker, "SPEAKER_00")


if __name__ == "__main__":
    unittest.main()
