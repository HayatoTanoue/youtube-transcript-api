import time
import json
from youtube_transcript_api import YouTubeTranscriptApi

def main():
    api = YouTubeTranscriptApi()
    
    # 実際のビデオIDリスト（短い動画を選択）
    video_ids = [
        'GJLlxj_dtq8',  # 短いテスト動画
        'dQw4w9WgXcQ',  # Rick Astley
        'jNQXAC9IVRw',  # 短い動画
    ]
    
    print("=== Integration Test: Parallel Transcript Fetching ===\n")
    
    # プログレストラッキング
    progress_log = []
    
    def track_progress(video_id, status):
        progress_log.append({
            'time': time.time(),
            'video_id': video_id,
            'status': status
        })
        print(f"[{time.strftime('%H:%M:%S')}] {video_id}: {status}")
    
    # 並列実行
    print("Starting parallel fetch...")
    start_time = time.time()
    
    results = api.fetch_parallel(
        video_ids,
        languages=['en'],
        max_workers=3,
        progress_callback=track_progress
    )
    
    elapsed = time.time() - start_time
    
    # 結果の分析
    print(f"\nCompleted in {elapsed:.2f} seconds\n")
    print("=== Results Summary ===")
    
    total_snippets = 0
    for video_id, result in results.items():
        if isinstance(result, Exception):
            print(f"❌ {video_id}: Failed - {type(result).__name__}")
        else:
            snippet_count = len(result.snippets)
            total_snippets += snippet_count
            print(f"✅ {video_id}: Success - {snippet_count} snippets")
    
    print(f"\nTotal snippets retrieved: {total_snippets}")
    print(f"Average time per video: {elapsed/len(video_ids):.2f}s")
    
    # 結果をJSONで保存
    output = {
        'execution_time': elapsed,
        'video_count': len(video_ids),
        'total_snippets': total_snippets,
        'progress_log': progress_log,
        'results': {
            vid: {'success': not isinstance(res, Exception), 
                  'snippet_count': len(res.snippets) if not isinstance(res, Exception) else 0}
            for vid, res in results.items()
        }
    }
    
    with open('verification/test-02-complex-feature/integration_results.json', 'w') as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
