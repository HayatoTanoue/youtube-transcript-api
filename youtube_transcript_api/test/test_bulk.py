from unittest import TestCase
import httpretty
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.test.test_api import load_asset


class TestBulk(TestCase):
    def setUp(self):
        httpretty.enable()
        httpretty.register_uri(
            httpretty.POST,
            "https://www.youtube.com/youtubei/v1/player",
            body=load_asset("youtube.innertube.json.static"),
        )
        httpretty.register_uri(
            httpretty.GET,
            "https://www.youtube.com/watch",
            body=load_asset("youtube.html.static"),
        )
        httpretty.register_uri(
            httpretty.GET,
            "https://www.youtube.com/api/timedtext",
            body=load_asset("transcript.xml.static"),
        )

    def tearDown(self):
        httpretty.reset()
        httpretty.disable()

    def test_fetch_bulk(self):
        api = YouTubeTranscriptApi()
        video_ids = [f"v{i}" for i in range(5)]
        results = api.fetch_bulk(video_ids)
        self.assertEqual(len(results), len(video_ids))
        self.assertGreaterEqual(len(httpretty.latest_requests()), 4)
