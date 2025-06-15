import unittest

from youtube_transcript_api import (
    FetchedTranscript,
    FetchedTranscriptSnippet,
    SearchResult,
)


class TestSearchInTranscript(unittest.TestCase):
    def setUp(self):
        self.transcript = FetchedTranscript(
            snippets=[
                FetchedTranscriptSnippet(
                    text="Hey, this is just a test", start=0.0, duration=1.54
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
            video_id="vid",
        )

    def test_search_keyword(self):
        results = self.transcript.search_in_transcript("test")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].matched_text.lower(), "test")
        self.assertAlmostEqual(results[0].start, 0.0)
        self.assertAlmostEqual(results[0].end, 1.54)

    def test_search_case_sensitive(self):
        results = self.transcript.search_in_transcript("Test", case_sensitive=True)
        self.assertEqual(len(results), 0)

    def test_search_regex(self):
        results = self.transcript.search_in_transcript(r"test\w+", regex=True)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].matched_text, "testing")

    def test_search_invalid_regex(self):
        with self.assertRaises(ValueError):
            self.transcript.search_in_transcript("([)", regex=True)


if __name__ == "__main__":
    unittest.main()
