# evaluation/scripts/test_bug_fix.py
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from youtube_transcript_api.formatters import WebVTTFormatter, SRTFormatter, FetchedTranscript, FetchedTranscriptSnippet
import re

def test_bug_fixes():
    """バグ修正の評価"""
    results = {
        "webvtt_time_format": False,
        "srt_index_start": False,
        "tests_updated": False,
        "commit_message": False,
        "no_regression": False
    }
    
    # テストデータ
    test_transcript = FetchedTranscript(
        snippets=[
            FetchedTranscriptSnippet(text="First line", start=0.0, duration=1.234),
            FetchedTranscriptSnippet(text="Second line", start=1.234, duration=2.567),
        ],
        language="English",
        language_code="en",
        is_generated=False,
        video_id="test123"
    )
    
    # 1. WebVTTフォーマットの確認
    webvtt_formatter = WebVTTFormatter()
    webvtt_output = webvtt_formatter.format_transcript(test_transcript)
    
    # 時間フォーマットの確認（HH:MM:SS.mmm）
    time_pattern = r'\d{2}:\d{2}:\d{2}\.\d{3}'
    if re.search(time_pattern, webvtt_output):
        results["webvtt_time_format"] = True
        print("✅ WebVTT time format is correct (using '.' separator)")
    else:
        print("❌ WebVTT time format is incorrect")
        print(f"Output sample: {webvtt_output.split('\\n')[2]}")
    
    # 2. SRTインデックスの確認
    srt_formatter = SRTFormatter()
    srt_output = srt_formatter.format_transcript(test_transcript)
    lines = srt_output.strip().split('\n')
    
    # 最初の行が"1"であることを確認
    if lines[0] == "1":
        results["srt_index_start"] = True
        print("✅ SRT index starts from 1")
    else:
        print(f"❌ SRT index incorrect. First line: '{lines[0]}'")
    
    # 3. テストファイルの更新確認
    test_file_path = "youtube_transcript_api/test/test_formatters.py"
    with open(test_file_path, 'r') as f:
        test_content = f.read()
        
        # WebVTTとSRTのテストが含まれているか
        if ("test_webvtt" in test_content.lower() and 
            "test_srt" in test_content.lower()):
            results["tests_updated"] = True
            print("✅ Test file contains relevant tests")
        else:
            print("❌ Test file missing WebVTT or SRT tests")
    
    # 4. 全体的な回帰テストの実行
    try:
        # 他のフォーマッターが正常に動作することを確認
        from youtube_transcript_api.formatters import JSONFormatter, TextFormatter
        
        json_formatter = JSONFormatter()
        text_formatter = TextFormatter()
        
        # 基本的な動作確認
        json_output = json_formatter.format_transcript(test_transcript)
        text_output = text_formatter.format_transcript(test_transcript)
        
        if json_output and text_output:
            results["no_regression"] = True
            print("✅ No regression in other formatters")
        else:
            print("❌ Regression detected in other formatters")
    except Exception as e:
        print(f"❌ Error during regression test: {e}")
    
    # 5. コミットメッセージの確認（gitログから）
    try:
        import subprocess
        git_log = subprocess.run(['git', 'log', '--oneline', '-n', '5'], 
                               capture_output=True, text=True)
        if "Fix formatting bugs" in git_log.stdout:
            results["commit_message"] = True
            print("✅ Appropriate commit message found")
        else:
            print("❌ Expected commit message not found")
    except:
        print("⚠️  Could not check git commit messages")
    
    return results

if __name__ == "__main__":
    results = test_bug_fixes()
    print("\n=== Bug Fix Evaluation Results ===")
    for key, value in results.items():
        status = "✅" if value else "❌"
        print(f"{status} {key}: {value}")
    
    success_rate = sum(results.values()) / len(results) * 100
    print(f"\nSuccess Rate: {success_rate:.1f}%")