# evaluation/scripts/run_all_tests.sh
#!/bin/bash
set -e

VERIFICATION_BASE="verification"

# 関数: 各検証の実行
run_verification() {
    local test_name=$1
    local test_dir="$VERIFICATION_BASE/$test_name"
    local branch_name="codex-$test_name"
    
    echo "=== Running verification: $test_name ==="
    
    # ブランチの確認
    if git show-ref --verify --quiet refs/heads/$branch_name; then
        git checkout $branch_name
    else
        echo "Branch $branch_name not found. Skipping..."
        return
    fi
    
    # テストの実行
    mkdir -p $test_dir
    
    # 基本テスト
    poetry run pytest youtube_transcript_api --cov=youtube_transcript_api \
        --cov-report=xml:$test_dir/coverage.xml \
        --cov-report=html:$test_dir/htmlcov \
        --cov-report=term | tee $test_dir/pytest_output.txt
    
    # Lint
    poetry run ruff check youtube_transcript_api | tee $test_dir/ruff_output.txt || true
    
    # 特定の評価スクリプトの実行
    case $test_name in
        "test-01-simple-feature")
            python evaluation/scripts/test_csv_formatter.py | tee $test_dir/feature_evaluation.txt
            ;;
        "test-02-complex-feature")
            python evaluation/scripts/test_parallel_feature.py | tee $test_dir/feature_evaluation.txt
            ;;
        "test-03-bug-fix")
            python evaluation/scripts/test_bug_fix.py | tee $test_dir/feature_evaluation.txt
            ;;
    esac
    
    # 差分の保存
    git diff main > $test_dir/changes.diff
    
    echo "Verification $test_name completed"
    echo ""
}

# メインに戻る
git checkout main

# 各検証の実行
for test in test-01-simple-feature test-02-complex-feature test-03-bug-fix; do
    run_verification $test
done

# 最終レポートの生成
python evaluation/scripts/generate_report.py

echo "All verifications completed!"