# バグ導入スクリプト
# evaluation/scripts/introduce_bug.py
import os

def introduce_bug():
    """formatters.pyにバグを導入"""
    file_path = "youtube_transcript_api/formatters.py"
    
    # バックアップ
    with open(file_path, 'r') as f:
        original_content = f.read()
    
    with open(file_path + '.backup', 'w') as f:
        f.write(original_content)
    
    # バグの導入：WebVTTFormatterの時間フォーマットを壊す
    buggy_content = original_content.replace(
        'return "{:02d}:{:02d}:{:02d}.{:03d}".format(hours, mins, secs, ms)',
        'return "{:02d}:{:02d}:{:02d},{:03d}".format(hours, mins, secs, ms)'  # カンマに変更（バグ）
    )
    
    # バグの導入2：SRTFormatterのインデックスを0始まりに
    buggy_content = buggy_content.replace(
        'return "{}\n{}\n{}".format(i + 1, time_text, snippet.text)',
        'return "{}\n{}\n{}".format(i, time_text, snippet.text)'  # インデックスのバグ
    )
    
    with open(file_path, 'w') as f:
        f.write(buggy_content)
    
    print("Bugs introduced successfully!")
    print("1. WebVTT formatter: time separator changed from '.' to ','")
    print("2. SRT formatter: index starts from 0 instead of 1")
    
    # コミットしてプッシュ
    os.system("git add -A")
    os.system('git commit -m "Introduce bugs for testing"')
    print("\nPlease push this commit to your fork for Codex to fix")

if __name__ == "__main__":
    introduce_bug()