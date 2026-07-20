import unittest

from repositories.artifact_repository import ArtifactRepository


class UserArtifactClassificationTests(unittest.TestCase):
    def test_accepts_explicit_user_ai_artifact(self):
        artifact = {"metadata": {"origin": "user_ai_request"}}
        self.assertTrue(ArtifactRepository.is_user_generated(artifact))

    def test_rejects_automatic_transcription_artifact(self):
        artifact = {
            "artifact_type": "speaker_transcript",
            "metadata": {"source": "meeting_video"},
        }
        self.assertFalse(ArtifactRepository.is_user_generated(artifact))

    def test_rejects_legacy_artifact_without_metadata(self):
        self.assertFalse(ArtifactRepository.is_user_generated({"artifact_type": "logs"}))


if __name__ == "__main__":
    unittest.main()
