from youtube_transcript_api import YouTubeTranscriptApi, VideoUnavailable
import json

api = YouTubeTranscriptApi()

# 存在しないビデオIDを含むリスト
video_ids = [
    'GJLlxj_dtq8',      # 正常
    'invalid_id_123',    # 無効
    'dQw4w9WgXcQ',      # 正常
]

print("Testing error handling...")
results = api.fetch_parallel(video_ids)

# 結果の分析
success_count = 0
error_count = 0

for video_id, result in results.items():
    if isinstance(result, Exception):
        error_count += 1
        print(f"❌ {video_id}: {type(result).__name__} - {str(result)}")
    else:
        success_count += 1
        print(f"✅ {video_id}: Success ({len(result.snippets)} snippets)")

print(f"\nSummary: {success_count} success, {error_count} errors")
print(f"Other videos continued despite errors: {'Yes' if success_count > 0 and error_count > 0 else 'No'}")
