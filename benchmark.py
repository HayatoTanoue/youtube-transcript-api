import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpretty
from youtube_transcript_api import YouTubeTranscriptApi

ASSETS = Path(__file__).resolve().parent / "youtube_transcript_api" / "test" / "assets"


def setup_mock():
    httpretty.enable()
    httpretty.register_uri(
        httpretty.POST,
        "https://www.youtube.com/youtubei/v1/player",
        body=(ASSETS / "youtube.innertube.json.static").read_bytes(),
    )
    httpretty.register_uri(
        httpretty.GET,
        "https://www.youtube.com/watch",
        body=(ASSETS / "youtube.html.static").read_bytes(),
    )
    httpretty.register_uri(
        httpretty.GET,
        "https://www.youtube.com/api/timedtext",
        body=(ASSETS / "transcript.xml.static").read_bytes(),
    )


def teardown_mock():
    httpretty.disable()
    httpretty.reset()


def benchmark_single(video_id: str) -> float:
    api = YouTubeTranscriptApi()
    start = time.perf_counter()
    api.fetch(video_id)
    return time.perf_counter() - start


def benchmark_multiple(video_ids) -> float:
    api = YouTubeTranscriptApi()
    start = time.perf_counter()
    with ThreadPoolExecutor() as ex:
        list(ex.map(api.fetch, video_ids))
    return time.perf_counter() - start


def benchmark_repeated(video_id: str, count: int = 10) -> float:
    api = YouTubeTranscriptApi()
    start = time.perf_counter()
    for _ in range(count):
        api.fetch(video_id)
    return time.perf_counter() - start


def main():
    setup_mock()
    vid = "GJLlxj_dtq8"
    single = benchmark_single(vid)
    parallel = benchmark_multiple([vid] * 10)
    cached = benchmark_repeated(vid)
    teardown_mock()

    print(f"Single fetch: {single:.4f}s")
    print(f"Parallel fetch of 10 videos: {parallel:.4f}s")
    print(f"Repeated fetch of same video (10x): {cached:.4f}s")


if __name__ == "__main__":
    main()
