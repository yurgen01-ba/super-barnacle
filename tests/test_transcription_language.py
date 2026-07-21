import os
import unittest
from unittest.mock import patch

from transcription.quality_config import (
    build_whisper_transcribe_kwargs,
    get_default_language,
)


class TranscriptionLanguageTests(unittest.TestCase):
    def test_language_is_automatic_when_no_explicit_default_exists(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PROJECT_BRAIN_TRANSCRIPTION_LANGUAGE", None)
            self.assertIsNone(get_default_language(None))
            self.assertNotIn("language", build_whisper_transcribe_kwargs(None))

    def test_explicit_language_is_forwarded_to_whisper(self):
        self.assertEqual("uk", get_default_language("uk"))
        self.assertEqual("uk", build_whisper_transcribe_kwargs("uk")["language"])


if __name__ == "__main__":
    unittest.main()
