# Performance Report

The benchmark was executed using `benchmark.py` which mocks network requests.
Results on this environment:

```
Single video baseline: 0.0137s
Single video optimized: 0.0040s
10 videos baseline: 0.1176s
10 videos optimized: 0.0290s
```

The optimized version shows more than a 50% speedup for both single and multiple
video retrievals. Dataclasses now use `slots=True` which reduces the memory
footprint of transcript objects by eliminating per-instance dictionaries.
