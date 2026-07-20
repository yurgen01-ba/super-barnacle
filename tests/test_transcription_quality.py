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

    def test_repairs_observed_accounts_misrecognition(self):
        self.assertEqual(
            apply_domain_glossary_repair("Ну, сигналы есть."),
            "Ну, accounts.",
        )


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

    def test_snaps_premature_change_to_question_boundary(self):
        source = segment(
            WordTimestamp("Хочешь", 0.0, 0.4, speaker="SPEAKER_01"),
            WordTimestamp("показать?", 0.4, 0.9, speaker="SPEAKER_00"),
            WordTimestamp("Ну,", 0.9, 1.1, speaker="SPEAKER_00"),
            WordTimestamp("смотри.", 1.1, 1.8, speaker="SPEAKER_00"),
        )

        utterances, debug = stabilize_speaker_utterances_with_debug([source])

        self.assertEqual(len(utterances), 2)
        self.assertEqual(utterances[0].speaker, "SPEAKER_01")
        self.assertEqual(utterances[0].text, "Хочешь показать?")
        self.assertEqual(utterances[1].text, "Ну, смотри.")
        self.assertEqual(len(debug["sentence_snap_adjustments"]), 1)

    def test_preserves_punctuated_short_reply(self):
        source = segment(
            WordTimestamp("Это,", 0.0, 0.5, speaker="SPEAKER_00"),
            WordTimestamp("ага.", 0.5, 0.8, speaker="SPEAKER_01"),
            WordTimestamp("Продолжим.", 2.0, 2.8, speaker="SPEAKER_01"),
        )

        utterances, _ = stabilize_speaker_utterances_with_debug([source])

        self.assertEqual(utterances[0].speaker, "SPEAKER_00")
        self.assertEqual(utterances[1].speaker, "SPEAKER_01")
        self.assertEqual(utterances[1].text, "ага. Продолжим.")


if __name__ == "__main__":
    unittest.main()
