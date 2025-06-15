import threading
import time
from youtube_transcript_api import YouTubeTranscriptApi

def test_concurrent_access():
    api = YouTubeTranscriptApi()
    results = {}
    errors = []
    
    def fetch_video(video_id, index):
        try:
            result = api.fetch(video_id)
            results[f"{video_id}_{index}"] = len(result.snippets)
        except Exception as e:
            errors.append((video_id, index, str(e)))
    
    # 複数スレッドから同時アクセス
    threads = []
    video_id = 'GJLlxj_dtq8'
    
    for i in range(10):
        t = threading.Thread(target=fetch_video, args=(video_id, i))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    print(f"Successful fetches: {len(results)}")
    print(f"Errors: {len(errors)}")
    print(f"Thread safety: {'PASS' if len(errors) == 0 else 'FAIL'}")
    
    if errors:
        for vid, idx, err in errors[:3]:  # 最初の3つのエラーを表示
            print(f"  Error in thread {idx}: {err}")

if __name__ == "__main__":
    test_concurrent_access()
