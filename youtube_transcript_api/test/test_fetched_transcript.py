import unittest
from youtube_transcript_api import FetchedTranscript, FetchedTranscriptSnippet


class TestFetchedTranscript(unittest.TestCase):
    def setUp(self):
        self.transcript = FetchedTranscript(
            snippets=[
                FetchedTranscriptSnippet(
                    text="Hey, this is just a test",
                    start=0.0,
                    duration=1.54,
                ),
                FetchedTranscriptSnippet(
                    text="this is not the original transcript",
                    start=1.54,
                    duration=4.16,
                ),
                FetchedTranscriptSnippet(
                    text="just something shorter, I made up for testing",
                    start=5.7,
                    duration=3.239,
                ),
            ],
            language="English",
            language_code="en",
            is_generated=False,
            video_id="GJLlxj_dtq8",
        )

    def test_get_summary_default(self):
        summary = self.transcript.get_summary()
        expected = (
            "Hey, this is just a test this is not the original transcript "
            "just something shorter, I made up for testing"
        )
        self.assertEqual(summary, expected)

    def test_get_summary_truncated(self):
        summary = self.transcript.get_summary(24)
        self.assertEqual(summary, "Hey, this is just a")

    def test_get_word_count(self):
        self.assertEqual(self.transcript.get_word_count(), 20)

    def test_get_duration(self):
        self.assertAlmostEqual(self.transcript.get_duration(), 8.939)


if __name__ == "__main__":
    unittest.main()
