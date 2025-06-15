# evaluation/scripts/test_csv_formatter.py
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from youtube_transcript_api.formatters import FormatterLoader, FetchedTranscript, FetchedTranscriptSnippet
import csv
from io import StringIO

def test_csv_formatter():
    """CSVフォーマッターの機能テスト"""
    results = {
        "formatter_exists": False,
        "correct_output": False,
        "headers_present": False,
        "cli_integration": False,
        "tests_added": False
    }
    
    # 1. フォーマッターの存在確認
    try:
        formatter = FormatterLoader().load('csv')
        results["formatter_exists"] = True
    except:
        print("❌ CSV formatter not found in FormatterLoader")
        return results
    
    # 2. 出力形式の確認
    test_transcript = FetchedTranscript(
        snippets=[
            FetchedTranscriptSnippet(text="Test line 1", start=0.0, duration=1.5),
            FetchedTranscriptSnippet(text="Test line 2", start=1.5, duration=2.0),
        ],
        language="English",
        language_code="en",
        is_generated=False,
        video_id="test123"
    )
    
    output = formatter.format_transcript(test_transcript)
    
    # CSV形式の検証
    reader = csv.DictReader(StringIO(output))
    rows = list(reader)
    
    # ヘッダーの確認
    expected_headers = {'start_time', 'end_time', 'duration', 'text'}
    if set(reader.fieldnames) == expected_headers:
        results["headers_present"] = True
        print("✅ CSV headers are correct")
    else:
        print(f"❌ CSV headers incorrect. Expected: {expected_headers}, Got: {set(reader.fieldnames)}")
    
    # データの確認
    if len(rows) == 2:
        row1 = rows[0]
        if (float(row1['start_time']) == 0.0 and 
            float(row1['end_time']) == 1.5 and
            float(row1['duration']) == 1.5 and
            row1['text'] == "Test line 1"):
            results["correct_output"] = True
            print("✅ CSV output format is correct")
        else:
            print("❌ CSV output data is incorrect")
    
    # 3. テストファイルの存在確認
    test_file_path = "youtube_transcript_api/test/test_formatters.py"
    with open(test_file_path, 'r') as f:
        content = f.read()
        if "csv" in content.lower() and "CSVFormatter" in content:
            results["tests_added"] = True
            print("✅ Tests for CSV formatter found")
        else:
            print("❌ No tests found for CSV formatter")
    
    return results

if __name__ == "__main__":
    results = test_csv_formatter()
    print("\n=== CSV Formatter Evaluation Results ===")
    for key, value in results.items():
        status = "✅" if value else "❌"
        print(f"{status} {key}: {value}")
    
    success_rate = sum(results.values()) / len(results) * 100
    print(f"\nSuccess Rate: {success_rate:.1f}%")