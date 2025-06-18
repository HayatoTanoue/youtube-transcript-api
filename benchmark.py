#!/usr/bin/env python3
"""
Performance benchmark script for YouTube Transcript API optimizations.
Measures single video, multiple video, and memory usage performance.
"""

import time
import tracemalloc
import statistics
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from youtube_transcript_api import YouTubeTranscriptApi


class PerformanceBenchmark:
    def __init__(self):
        self.test_video_ids = [
            "GJLlxj_dtq8",  # Test video from existing tests
            "dQw4w9WgXcQ",  # Rick Roll (popular video)
            "9bZkp7q19f0",  # Gangnam Style
            "kJQP7kiw5Fk",  # Despacito
            "fJ9rUzIMcZQ",  # Bohemian Rhapsody
            "YQHsXMglC9A",  # Hello - Adele
            "CevxZvSJLk8",  # Katy Perry - Roar
            "hTWKbfoikeg",  # Smells Like Teen Spirit
            "QDYfEBY9NM4",  # Linkin Park - In The End
            "60ItHLz5WEA",  # Alan Walker - Faded
        ]
        self.results = {}

    def measure_memory_usage(self, func, *args, **kwargs):
        """Measure peak memory usage of a function."""
        tracemalloc.start()
        try:
            result = func(*args, **kwargs)
            current, peak = tracemalloc.get_traced_memory()
            return result, peak
        finally:
            tracemalloc.stop()

    def benchmark_single_video(self, video_id: str, runs: int = 3) -> Dict[str, Any]:
        """Benchmark single video transcript fetching."""
        times = []
        memory_peaks = []
        
        for _ in range(runs):
            api = YouTubeTranscriptApi()
            
            start_time = time.time()
            try:
                transcript, peak_memory = self.measure_memory_usage(
                    api.fetch, video_id
                )
                end_time = time.time()
                
                times.append(end_time - start_time)
                memory_peaks.append(peak_memory)
                
            except Exception as e:
                print(f"Error fetching transcript for {video_id}: {e}")
                continue
        
        if not times:
            return {"error": "No successful runs"}
            
        return {
            "avg_time": statistics.mean(times),
            "min_time": min(times),
            "max_time": max(times),
            "avg_memory": statistics.mean(memory_peaks),
            "peak_memory": max(memory_peaks),
            "runs": len(times)
        }

    def benchmark_multiple_videos_sequential(self, video_ids: List[str]) -> Dict[str, Any]:
        """Benchmark multiple videos fetched sequentially."""
        start_time = time.time()
        
        try:
            results, peak_memory = self.measure_memory_usage(
                self._fetch_videos_sequential, video_ids
            )
            end_time = time.time()
            
            return {
                "total_time": end_time - start_time,
                "peak_memory": peak_memory,
                "successful_fetches": len([r for r in results if r is not None]),
                "total_videos": len(video_ids)
            }
        except Exception as e:
            return {"error": str(e)}

    def benchmark_multiple_videos_parallel(self, video_ids: List[str], max_workers: int = 4) -> Dict[str, Any]:
        """Benchmark multiple videos fetched in parallel."""
        start_time = time.time()
        
        try:
            results, peak_memory = self.measure_memory_usage(
                self._fetch_videos_parallel, video_ids, max_workers
            )
            end_time = time.time()
            
            return {
                "total_time": end_time - start_time,
                "peak_memory": peak_memory,
                "successful_fetches": len([r for r in results if r is not None]),
                "total_videos": len(video_ids),
                "max_workers": max_workers
            }
        except Exception as e:
            return {"error": str(e)}

    def _fetch_videos_sequential(self, video_ids: List[str]) -> List[Any]:
        """Fetch videos sequentially."""
        api = YouTubeTranscriptApi()
        results = []
        
        for video_id in video_ids:
            try:
                transcript = api.fetch(video_id)
                results.append(transcript)
            except Exception as e:
                print(f"Error fetching {video_id}: {e}")
                results.append(None)
                
        return results

    def _fetch_videos_parallel(self, video_ids: List[str], max_workers: int) -> List[Any]:
        """Fetch videos in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(self._fetch_single_video, video_id): i 
                for i, video_id in enumerate(video_ids)
            }
            
            result_dict = {}
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    result_dict[index] = future.result()
                except Exception as e:
                    print(f"Error fetching video {video_ids[index]}: {e}")
                    result_dict[index] = None
            
            for i in range(len(video_ids)):
                results.append(result_dict.get(i, None))
                    
        return results

    def _fetch_single_video(self, video_id: str):
        """Fetch a single video transcript."""
        api = YouTubeTranscriptApi()
        return api.fetch(video_id)

    def run_full_benchmark(self) -> Dict[str, Any]:
        """Run complete benchmark suite."""
        print("Starting performance benchmark...")
        
        print("Benchmarking single video performance...")
        single_video_result = self.benchmark_single_video(self.test_video_ids[0])
        
        print("Benchmarking multiple videos (sequential)...")
        sequential_result = self.benchmark_multiple_videos_sequential(self.test_video_ids)
        
        print("Benchmarking multiple videos (parallel)...")
        parallel_result = self.benchmark_multiple_videos_parallel(self.test_video_ids)
        
        results = {
            "single_video": single_video_result,
            "multiple_videos_sequential": sequential_result,
            "multiple_videos_parallel": parallel_result,
            "test_video_count": len(self.test_video_ids),
            "timestamp": time.time()
        }
        
        return results

    def save_results(self, results: Dict[str, Any], filename: str):
        """Save benchmark results to JSON file."""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {filename}")

    def print_summary(self, results: Dict[str, Any]):
        """Print benchmark summary."""
        print("\n" + "="*50)
        print("BENCHMARK SUMMARY")
        print("="*50)
        
        if "single_video" in results and "error" not in results["single_video"]:
            sv = results["single_video"]
            print(f"Single Video Performance:")
            print(f"  Average Time: {sv['avg_time']:.3f}s")
            print(f"  Peak Memory: {sv['peak_memory'] / 1024 / 1024:.2f} MB")
        
        if "multiple_videos_sequential" in results and "error" not in results["multiple_videos_sequential"]:
            seq = results["multiple_videos_sequential"]
            print(f"\nMultiple Videos (Sequential):")
            print(f"  Total Time: {seq['total_time']:.3f}s")
            print(f"  Peak Memory: {seq['peak_memory'] / 1024 / 1024:.2f} MB")
            print(f"  Success Rate: {seq['successful_fetches']}/{seq['total_videos']}")
        
        if "multiple_videos_parallel" in results and "error" not in results["multiple_videos_parallel"]:
            par = results["multiple_videos_parallel"]
            print(f"\nMultiple Videos (Parallel):")
            print(f"  Total Time: {par['total_time']:.3f}s")
            print(f"  Peak Memory: {par['peak_memory'] / 1024 / 1024:.2f} MB")
            print(f"  Success Rate: {par['successful_fetches']}/{par['total_videos']}")
            
            if "multiple_videos_sequential" in results and "error" not in results["multiple_videos_sequential"]:
                speedup = results["multiple_videos_sequential"]["total_time"] / par["total_time"]
                print(f"  Speedup vs Sequential: {speedup:.2f}x")


def main():
    """Main benchmark execution."""
    benchmark = PerformanceBenchmark()
    
    results = benchmark.run_full_benchmark()
    
    benchmark.save_results(results, "benchmark_results.json")
    benchmark.print_summary(results)
    
    return results


if __name__ == "__main__":
    main()
