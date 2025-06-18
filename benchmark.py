import argparse
import time
import tracemalloc
from concurrent.futures import ThreadPoolExecutor

from youtube_transcript_api import YouTubeTranscriptApi


def measure_single(video_id: str, runs: int = 3):
    times = []
    memories = []
    for _ in range(runs):
        start = time.perf_counter()
        tracemalloc.start()
        YouTubeTranscriptApi().fetch(video_id)
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        times.append(time.perf_counter() - start)
        memories.append(peak)
    return sum(times) / len(times), max(memories)


def measure_multiple(video_ids, runs: int = 3):
    times = []
    memories = []
    for _ in range(runs):
        start = time.perf_counter()
        tracemalloc.start()
        with ThreadPoolExecutor(max_workers=len(video_ids)) as ex:
            list(ex.map(lambda vid: YouTubeTranscriptApi().fetch(vid), video_ids))
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        times.append(time.perf_counter() - start)
        memories.append(peak)
    return sum(times) / len(times), max(memories)


def main():
    parser = argparse.ArgumentParser(description="Benchmark YouTube Transcript retrieval")
    parser.add_argument("video_ids", nargs='+', help="Video IDs to benchmark")
    args = parser.parse_args()

    single_time, single_mem = measure_single(args.video_ids[0])
    multi_time, multi_mem = measure_multiple(args.video_ids[:10])

    print("Single video: {:.2f}s, peak memory {:.2f}KB".format(single_time, single_mem / 1024))
    print("10 videos: {:.2f}s, peak memory {:.2f}KB".format(multi_time, multi_mem / 1024))


if __name__ == "__main__":
    main()
