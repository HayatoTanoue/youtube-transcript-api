import unittest
from youtube_transcript_api import (
    FetchedTranscript,
    FetchedTranscriptSnippet,
    SearchResult,
)


class TestSearchFunctionality(unittest.TestCase):
    def setUp(self):
        self.transcript = FetchedTranscript(
            snippets=[
                FetchedTranscriptSnippet(
                    text="Hello world, this is a test",
                    start=0.0,
                    duration=2.0,
                ),
                FetchedTranscriptSnippet(
                    text="Python programming is awesome",
                    start=2.0,
                    duration=3.0,
                ),
                FetchedTranscriptSnippet(
                    text="Machine learning and artificial intelligence",
                    start=5.0,
                    duration=4.0,
                ),
                FetchedTranscriptSnippet(
                    text="Hello again, testing search functionality",
                    start=9.0,
                    duration=3.0,
                ),
            ],
            language="English",
            language_code="en",
            is_generated=False,
            video_id="test_video",
        )

    def test_basic_search_case_insensitive(self):
        """Test basic case-insensitive search."""
        results = self.transcript.search_in_transcript("hello")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].matched_text, "Hello")
        self.assertEqual(results[0].start_time, 0.0)
        self.assertEqual(results[0].end_time, 2.0)
        self.assertEqual(results[1].matched_text, "Hello")
        self.assertEqual(results[1].start_time, 9.0)
        self.assertEqual(results[1].end_time, 12.0)

    def test_basic_search_case_sensitive(self):
        """Test case-sensitive search."""
        results = self.transcript.search_in_transcript("hello", case_sensitive=True)
        self.assertEqual(len(results), 0)

        results = self.transcript.search_in_transcript("Hello", case_sensitive=True)
        self.assertEqual(len(results), 2)

    def test_regex_search(self):
        """Test regular expression search."""
        results = self.transcript.search_in_transcript(
            r"[Pp]ython|[Mm]achine", use_regex=True
        )
        self.assertEqual(len(results), 2)
        self.assertIn("Python", results[0].matched_text)
        self.assertIn("Machine", results[1].matched_text)

    def test_invalid_regex(self):
        """Test invalid regular expression handling."""
        with self.assertRaises(ValueError) as cm:
            self.transcript.search_in_transcript("[invalid", use_regex=True)
        self.assertIn("Invalid regular expression pattern", str(cm.exception))

    def test_no_results(self):
        """Test search with no results."""
        results = self.transcript.search_in_transcript("nonexistent")
        self.assertEqual(len(results), 0)

    def test_context_extraction(self):
        """Test context extraction around matches."""
        results = self.transcript.search_in_transcript("programming")
        self.assertEqual(len(results), 1)
        self.assertIn("Python programming is awesome", results[0].context)

    def test_search_result_dataclass(self):
        """Test SearchResult dataclass properties."""
        results = self.transcript.search_in_transcript("test")
        self.assertGreater(len(results), 0)
        result = results[0]
        self.assertIsInstance(result, SearchResult)
        self.assertIsInstance(result.matched_text, str)
        self.assertIsInstance(result.start_time, float)
        self.assertIsInstance(result.end_time, float)
        self.assertIsInstance(result.context, str)

    def test_phrase_search(self):
        """Test searching for phrases."""
        results = self.transcript.search_in_transcript("artificial intelligence")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].matched_text, "artificial intelligence")

    def test_empty_search_term(self):
        """Test empty search term."""
        results = self.transcript.search_in_transcript("")
        self.assertEqual(len(results), 0)

    def test_whitespace_only_search_term(self):
        """Test whitespace-only search term."""
        results = self.transcript.search_in_transcript("   ")
        self.assertEqual(len(results), 0)

    def test_special_characters_in_search(self):
        """Test search with special characters."""
        transcript_with_special = FetchedTranscript(
            snippets=[
                FetchedTranscriptSnippet(
                    text="Price is $100.50 (fifty cents)",
                    start=0.0,
                    duration=2.0,
                ),
            ],
            language="English",
            language_code="en",
            is_generated=False,
            video_id="test_video",
        )
        results = transcript_with_special.search_in_transcript("$100.50")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].matched_text, "$100.50")

    def test_regex_case_sensitive(self):
        """Test regex search with case sensitivity."""
        results = self.transcript.search_in_transcript(
            r"hello", use_regex=True, case_sensitive=True
        )
        self.assertEqual(len(results), 0)

        results = self.transcript.search_in_transcript(
            r"Hello", use_regex=True, case_sensitive=True
        )
        self.assertEqual(len(results), 2)

    def test_regex_case_insensitive(self):
        """Test regex search case insensitive."""
        results = self.transcript.search_in_transcript(
            r"hello", use_regex=True, case_sensitive=False
        )
        self.assertEqual(len(results), 2)

    def test_multiple_matches_same_snippet(self):
        """Test multiple matches in the same snippet."""
        transcript_with_repeats = FetchedTranscript(
            snippets=[
                FetchedTranscriptSnippet(
                    text="test test test",
                    start=0.0,
                    duration=2.0,
                ),
            ],
            language="English",
            language_code="en",
            is_generated=False,
            video_id="test_video",
        )
        results = transcript_with_repeats.search_in_transcript("test")
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertEqual(result.start_time, 0.0)
            self.assertEqual(result.end_time, 2.0)

    def test_context_boundary_handling(self):
        """Test context extraction at word boundaries."""
        short_transcript = FetchedTranscript(
            snippets=[
                FetchedTranscriptSnippet(
                    text="one two three",
                    start=0.0,
                    duration=1.0,
                ),
            ],
            language="English",
            language_code="en",
            is_generated=False,
            video_id="test_video",
        )
        results = short_transcript.search_in_transcript("two")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].context, "one two three")

    def test_empty_transcript(self):
        """Test search on empty transcript."""
        empty_transcript = FetchedTranscript(
            snippets=[],
            language="English",
            language_code="en",
            is_generated=False,
            video_id="test_video",
        )
        results = empty_transcript.search_in_transcript("test")
        self.assertEqual(len(results), 0)

    def test_transcript_with_empty_snippets(self):
        """Test search on transcript with empty text snippets."""
        transcript_with_empty = FetchedTranscript(
            snippets=[
                FetchedTranscriptSnippet(
                    text="",
                    start=0.0,
                    duration=1.0,
                ),
                FetchedTranscriptSnippet(
                    text="hello world",
                    start=1.0,
                    duration=2.0,
                ),
            ],
            language="English",
            language_code="en",
            is_generated=False,
            video_id="test_video",
        )
        results = transcript_with_empty.search_in_transcript("hello")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].start_time, 1.0)
