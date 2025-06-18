from unittest import TestCase
from unittest.mock import patch

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._transcripts import TranscriptListFetcher


class TestCaching(TestCase):
    def test_list_caching(self):
        with patch.object(TranscriptListFetcher, "fetch", return_value="data") as fetch:
            api = YouTubeTranscriptApi()
            self.assertEqual(api.list("id"), "data")
            self.assertEqual(api.list("id"), "data")
            self.assertEqual(fetch.call_count, 1)
