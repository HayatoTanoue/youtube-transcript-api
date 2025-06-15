# evaluation/scripts/generate_report.py
import os
import json
from datetime import datetime
import xml.etree.ElementTree as ET

def parse_coverage(xml_path):
    """カバレッジXMLをパース"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        return float(root.attrib.get('line-rate', 0)) * 100
    except:
        return 0

def generate_report():
    """統合レポートの生成"""
    report = {
        "execution_date": datetime.now().isoformat(),
        "verifications": {}
    }
    
    verification_dirs = [
        "test-01-simple-feature",
        "test-02-complex-feature", 
        "test-03-bug-fix"
    ]
    
    for test_name in verification_dirs:
        test_dir = f"verification/{test_name}"
        if not os.path.exists(test_dir):
            continue
            
        verification_data = {
            "coverage": parse_coverage(f"{test_dir}/coverage.xml"),
            "tests_passed": False,
            "lint_issues": 0,
            "feature_evaluation": {}
        }
        
        # PyTestの結果
        if os.path.exists(f"{test_dir}/pytest_output.txt"):
            with open(f"{test_dir}/pytest_output.txt", 'r') as f:
                content = f.read()
                if "failed" not in content and "error" not in content:
                    verification_data["tests_passed"] = True
        
        # Lintの結果
        if os.path.exists(f"{test_dir}/ruff_output.txt"):
            with open(f"{test_dir}/ruff_output.txt", 'r') as f:
                content = f.read()
                verification_data["lint_issues"] = content.count("E") + content.count("F")
        
        # 機能評価の結果
        if os.path.exists(f"{test_dir}/feature_evaluation.txt"):
            with open(f"{test_dir}/feature_evaluation.txt", 'r') as f:
                content = f.read()
                # Success Rateを抽出
                if "Success Rate:" in content:
                    rate_line = [l for l in content.split('\n') if "Success Rate:" in l][0]
                    verification_data["feature_success_rate"] = rate_line.split(":")[1].strip()
        
        report["verifications"][test_name] = verification_data
    
    # レポートの保存
    with open("verification/final_report.json", 'w') as f:
        json.dump(report, f, indent=2)
    
    # Markdownレポートの生成
    generate_markdown_report(report)

def generate_markdown_report(report):
    """Markdownフォーマットのレポート生成"""
    md_content = f"""# Codex検証結果レポート

実行日時: {report['execution_date']}

## サマリー

| 検証項目 | カバレッジ | テスト | Lint | 機能評価 |
|---------|-----------|-------|------|---------|
"""
    
    for test_name, data in report['verifications'].items():
        test_status = "✅" if data['tests_passed'] else "❌"
        lint_status = "✅" if data['lint_issues'] == 0 else f"⚠️ ({data['lint_issues']})"
        success_rate = data.get('feature_success_rate', 'N/A')
        
        md_content += f"| {test_name} | {data['coverage']:.1f}% | {test_status} | {lint_status} | {success_rate} |\n"
    
    md_content += """
## 詳細結果

各検証の詳細は以下のディレクトリを参照:
- `verification/test-01-simple-feature/`
- `verification/test-02-complex-feature/`
- `verification/test-03-bug-fix/`

## 定性評価

### コード品質
- [ ] 既存のコーディングスタイルに準拠
- [ ] 適切なエラーハンドリング
- [ ] ドキュメント/コメントの充実度
- [ ] テストの網羅性

### 保守性
- [ ] コードの可読性
- [ ] モジュール性
- [ ] 既存機能への影響なし

## 結論

[ここに総合的な評価を記載]
"""
    
    with open("verification/final_report.md", 'w') as f:
        f.write(md_content)

if __name__ == "__main__":
    generate_report()
    print("Report generated: verification/final_report.md")