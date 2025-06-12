import unittest
from youtube_transcript_api import FetchedTranscript, FetchedTranscriptSnippet


class TestFetchedTranscriptFiltering(unittest.TestCase):
    def setUp(self):
        self.transcript = FetchedTranscript(
            snippets=[
                FetchedTranscriptSnippet(text="first snippet", start=0.0, duration=1.0),
                FetchedTranscriptSnippet(
                    text="second snippet", start=1.5, duration=1.0
                ),
                FetchedTranscriptSnippet(text="third keyword", start=3.0, duration=2.0),
            ],
            language="English",
            language_code="en",
            is_generated=False,
            video_id="vid",
        )

    def test_filter_by_time_range(self):
        filtered = self.transcript.filter_by_time_range(1.0, 3.1)
        self.assertEqual(len(filtered), 2)
        self.assertEqual(filtered[0].text, "second snippet")
        self.assertEqual(filtered[1].text, "third keyword")

    def test_filter_by_time_range_empty(self):
        filtered = self.transcript.filter_by_time_range(5.0, 6.0)
        self.assertEqual(len(filtered), 0)

    def test_filter_by_keyword(self):
        filtered = self.transcript.filter_by_keyword("keyword")
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].text, "third keyword")

    def test_filter_by_keyword_case_sensitive(self):
        filtered = self.transcript.filter_by_keyword("Keyword", case_sensitive=True)
        self.assertEqual(len(filtered), 0)

    def test_merge_continuous_snippets(self):
        merged = self.transcript.merge_continuous_snippets()
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0].text, "first snippet second snippet third keyword")
        self.assertAlmostEqual(merged[0].duration, 5.0)

    def test_merge_continuous_snippets_empty(self):
        empty = FetchedTranscript(
            snippets=[],
            language="en",
            language_code="en",
            is_generated=False,
            video_id="vid",
        )
        merged = empty.merge_continuous_snippets()
        self.assertEqual(len(merged), 0)


if __name__ == "__main__":
    unittest.main()
