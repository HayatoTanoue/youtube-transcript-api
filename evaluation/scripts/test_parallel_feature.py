# evaluation/scripts/test_parallel_feature.py
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from youtube_transcript_api import YouTubeTranscriptApi, VideoUnavailable
import time
import threading
from unittest.mock import Mock, patch

def test_parallel_feature():
    """並列処理機能の評価"""
    results = {
        "method_exists": False,
        "parallel_execution": False,
        "error_handling": False,
        "progress_callback": False,
        "cli_integration": False,
        "tests_added": False,
        "documentation": False,
        "thread_safety": False
    }
    
    # 1. メソッドの存在確認
    api = YouTubeTranscriptApi()
    if hasattr(api, 'fetch_parallel'):
        results["method_exists"] = True
        print("✅ fetch_parallel method exists")
    else:
        print("❌ fetch_parallel method not found")
        return results
    
    # 2. 並列実行のテスト（モック使用）
    with patch.object(api, 'fetch') as mock_fetch:
        # fetchメソッドに遅延を追加してシミュレート
        def delayed_fetch(video_id, *args, **kwargs):
            time.sleep(0.1)
            return Mock(video_id=video_id)
        
        mock_fetch.side_effect = delayed_fetch
        
        video_ids = ['video1', 'video2', 'video3']
        start_time = time.time()
        
        try:
            results_dict = api.fetch_parallel(video_ids, max_workers=3)
            elapsed_time = time.time() - start_time
            
            # 並列実行の確認（3つの0.1秒の処理が0.3秒未満で完了）
            if elapsed_time < 0.25 and len(results_dict) == 3:
                results["parallel_execution"] = True
                print(f"✅ Parallel execution confirmed (elapsed: {elapsed_time:.2f}s)")
            else:
                print(f"❌ Parallel execution not working properly (elapsed: {elapsed_time:.2f}s)")
        except Exception as e:
            print(f"❌ Error in parallel execution: {e}")
    
    # 3. エラーハンドリングのテスト
    with patch.object(api, 'fetch') as mock_fetch:
        def fetch_with_error(video_id, *args, **kwargs):
            if video_id == 'error_video':
                raise VideoUnavailable(video_id)
            return Mock(video_id=video_id)
        
        mock_fetch.side_effect = fetch_with_error
        
        try:
            results_dict = api.fetch_parallel(['video1', 'error_video', 'video2'])
            
            if (isinstance(results_dict.get('error_video'), Exception) and
                results_dict.get('video1') is not None and
                results_dict.get('video2') is not None):
                results["error_handling"] = True
                print("✅ Error handling works correctly")
            else:
                print("❌ Error handling not implemented properly")
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
    
    # 4. プログレスコールバックのテスト
    progress_calls = []
    def progress_callback(video_id, status):
        progress_calls.append((video_id, status))
    
    try:
        with patch.object(api, 'fetch') as mock_fetch:
            mock_fetch.return_value = Mock(video_id='test')
            
            # progress_callback引数の確認
            try:
                api.fetch_parallel(['video1'], progress_callback=progress_callback)
                if len(progress_calls) > 0:
                    results["progress_callback"] = True
                    print("✅ Progress callback implemented")
            except TypeError:
                print("❌ Progress callback not implemented")
    except:
        pass
    
    # 5. CLIオプションの確認
    cli_file_path = "youtube_transcript_api/_cli.py"
    with open(cli_file_path, 'r') as f:
        cli_content = f.read()
        if "--parallel" in cli_content or "parallel" in cli_content.lower():
            results["cli_integration"] = True
            print("✅ CLI integration found")
        else:
            print("❌ CLI integration not found")
    
    # 6. テストの確認
    test_file_path = "youtube_transcript_api/test/test_api.py"
    with open(test_file_path, 'r') as f:
        test_content = f.read()
        if "parallel" in test_content.lower() and "fetch_parallel" in test_content:
            results["tests_added"] = True
            print("✅ Tests for parallel feature found")
        else:
            print("❌ No tests found for parallel feature")
    
    # 7. ドキュメントの確認
    readme_path = "README.md"
    with open(readme_path, 'r') as f:
        readme_content = f.read()
        if "parallel" in readme_content.lower() or "fetch_parallel" in readme_content:
            results["documentation"] = True
            print("✅ Documentation updated")
        else:
            print("❌ Documentation not updated")
    
    return results

if __name__ == "__main__":
    results = test_parallel_feature()
    print("\n=== Parallel Feature Evaluation Results ===")
    for key, value in results.items():
        status = "✅" if value else "❌"
        print(f"{status} {key}: {value}")
    
    success_rate = sum(results.values()) / len(results) * 100
    print(f"\nSuccess Rate: {success_rate:.1f}%")