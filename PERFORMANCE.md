# Performance Improvement Report

The transcript fetching logic was optimized to reduce latency and memory usage.
Benchmarks were executed using `benchmark.py` with mocked network responses.

| Scenario | Old Time (s) | New Time (s) |
|---------|--------------|--------------|
| Single video fetch | 0.0252 | 0.0132 |
| Parallel fetch of 10 videos | 0.3446 | 0.1649 |
| Repeated fetch of same video (10x) | 0.1643 | 0.0246 |

The new implementation introduces connection pooling, gzip compression support,
and an in-memory LRU cache for transcript lists. Dataclasses now use `slots` to
reduce memory footprint.
