# Performance Improvements

This release introduces several optimisations to subtitle retrieval.

## Summary

- **Caching**: `YouTubeTranscriptApi.list` now caches transcript list results to
  avoid duplicate network requests.
- **Concurrent Fetching**: `get_transcripts` uses a thread pool to download
  transcripts in parallel.
- **Memory Optimisations**: Transcript data classes make use of `__slots__` to
  reduce per-instance overhead and the HTML parsing regex is cached.

## Benchmark

Use `benchmark.py` to measure the runtime and peak memory usage.

```bash
python benchmark.py <video_id> [more video ids]
```

The script prints metrics for a single video and the first ten provided video
IDs.
