import unittest

from services.speaker_sample_service import select_speaker_windows


class SpeakerSampleServiceTests(unittest.TestCase):
    def test_detects_count_from_diarization_and_uses_longest_utterance(self):
        result = {
            "duration_seconds": 30,
            "audio_intelligence": {
                "speaker_utterances": [
                    {"speaker": "SPEAKER_00", "start": 1, "end": 2},
                    {"speaker": "SPEAKER_01", "start": 6, "end": 9},
                    {"speaker": "SPEAKER_00", "start": 15, "end": 21},
                ]
            },
        }

        windows = select_speaker_windows(result)

        self.assertEqual([item["speaker"] for item in windows], ["SPEAKER_00", "SPEAKER_01"])
        self.assertEqual(windows[0]["duration"], 5.0)
        self.assertGreater(windows[0]["start"], 15.0)

    def test_uses_transcript_segments_as_fallback(self):
        result = {
            "duration_seconds": 8,
            "transcript_segments": [
                {"speaker": "SPEAKER_02", "start": 0, "end": 4},
            ],
        }
        windows = select_speaker_windows(result)
        self.assertEqual(len(windows), 1)
        self.assertEqual(windows[0]["speaker"], "SPEAKER_02")
        self.assertEqual(windows[0]["duration"], 5.0)


if __name__ == "__main__":
    unittest.main()
