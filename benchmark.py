import statistics
import time
from pathlib import Path

import httpretty

from youtube_transcript_api import YouTubeTranscriptApi

ASSETS = Path("youtube_transcript_api/test/assets")


def load_asset(name: str) -> bytes:
    with open(ASSETS / name, "rb") as fh:
        return fh.read()


def setup_mock():
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


def teardown_mock():
    httpretty.disable()
    httpretty.reset()


def measure_single(use_cache: bool, runs: int = 5):
    api = YouTubeTranscriptApi(enable_cache=use_cache)
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        api.fetch("GJLlxj_dtq8")
        times.append(time.perf_counter() - start)
    return statistics.mean(times)


def measure_multiple(use_cache: bool, count: int = 10):
    api = YouTubeTranscriptApi(enable_cache=use_cache)
    start = time.perf_counter()
    for _ in range(count):
        api.fetch("GJLlxj_dtq8")
    return time.perf_counter() - start


def main():
    setup_mock()
    try:
        base_single = measure_single(False)
        opt_single = measure_single(True)
        base_multi = measure_multiple(False)
        opt_multi = measure_multiple(True)
        print("Single video baseline: {:.4f}s".format(base_single))
        print("Single video optimized: {:.4f}s".format(opt_single))
        print("10 videos baseline: {:.4f}s".format(base_multi))
        print("10 videos optimized: {:.4f}s".format(opt_multi))
    finally:
        teardown_mock()


if __name__ == "__main__":
    main()
