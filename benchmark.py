import time
import tracemalloc
from pathlib import Path
import httpretty
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.test.test_api import load_asset

ASSETS = Path('youtube_transcript_api/test/assets')

VIDEO_IDS = [f"vid{i}" for i in range(10)]


def setup_mock():
    httpretty.enable()
    httpretty.register_uri(httpretty.POST, "https://www.youtube.com/youtubei/v1/player", body=load_asset("youtube.innertube.json.static"))
    httpretty.register_uri(httpretty.GET, "https://www.youtube.com/watch", body=load_asset("youtube.html.static"))
    httpretty.register_uri(httpretty.GET, "https://www.youtube.com/api/timedtext", body=load_asset("transcript.xml.static"))


def teardown_mock():
    httpretty.reset()
    httpretty.disable()


def bench_single(api: YouTubeTranscriptApi, video_id: str):
    start = time.perf_counter()
    tracemalloc.start()
    api.fetch(video_id)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return time.perf_counter() - start, peak


def bench_bulk(api: YouTubeTranscriptApi, video_ids):
    start = time.perf_counter()
    tracemalloc.start()
    api.fetch_bulk(video_ids)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    return time.perf_counter() - start, peak


def main():
    setup_mock()
    api = YouTubeTranscriptApi()
    single = bench_single(api, VIDEO_IDS[0])
    bulk = bench_bulk(api, VIDEO_IDS)
    teardown_mock()
    print(f"Single fetch: {single[0]:.4f}s, Peak memory: {single[1]/1024:.1f} KiB")
    print(f"Bulk fetch: {bulk[0]:.4f}s, Peak memory: {bulk[1]/1024:.1f} KiB")


if __name__ == "__main__":
    main()
