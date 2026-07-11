from __future__ import annotations

import unittest

from transcription.audio_contracts import TranscriptSegment, WordTimestamp
from transcription.domain_glossary import apply_domain_glossary_repair
from transcription.speaker_utterance_stabilizer import (
    stabilize_speaker_utterances_with_debug,
)


def segment(*words: WordTimestamp) -> TranscriptSegment:
    return TranscriptSegment(
        id=0,
        start=float(words[0].start or 0),
        end=float(words[-1].end or 0),
        text=" ".join(word.word for word in words),
        words=list(words),
    )


class DomainGlossaryTests(unittest.TestCase):
    def test_repairs_domain_terms_and_whitespace(self):
        repaired = apply_domain_glossary_repair(
            "джира   таск, саммари и аккаунтс"
        )

        self.assertEqual(repaired, "Jira task, summary и accounts")


class SpeakerBoundaryTests(unittest.TestCase):
    def test_preserves_one_word_reply_without_pause(self):
        source = segment(
            WordTimestamp("Смотри.", 0.0, 1.0, speaker="SPEAKER_00"),
            WordTimestamp("Да.", 1.0, 1.25, speaker="SPEAKER_01"),
            WordTimestamp("Продолжай.", 1.25, 2.0, speaker="SPEAKER_00"),
        )

        utterances, debug = stabilize_speaker_utterances_with_debug([source])

        self.assertEqual(
            [item.speaker for item in utterances],
            ["SPEAKER_00", "SPEAKER_01", "SPEAKER_00"],
        )
        self.assertEqual(utterances[1].text, "Да.")
        self.assertEqual(debug["rejected_boundaries"], 0)

    def test_preserves_overlapping_interruption(self):
        source = segment(
            WordTimestamp("Она", 0.0, 0.6, speaker="SPEAKER_00"),
            WordTimestamp("готова.", 0.6, 1.0, speaker="SPEAKER_00"),
            WordTimestamp("Хочешь", 0.9, 1.2, speaker="SPEAKER_01"),
            WordTimestamp("показать?", 1.2, 1.8, speaker="SPEAKER_01"),
        )

        utterances, _ = stabilize_speaker_utterances_with_debug([source])

        self.assertEqual(len(utterances), 2)
        self.assertEqual(utterances[1].speaker, "SPEAKER_01")
        self.assertEqual(utterances[1].text, "Хочешь показать?")


if __name__ == "__main__":
    unittest.main()
