#!/bin/bash
set -e

OUTPUT_DIR="verification/common/baseline"
mkdir -p $OUTPUT_DIR

echo "=== Running baseline tests ==="

# pytest実行
poetry run pytest youtube_transcript_api --cov=youtube_transcript_api --cov-report=xml:$OUTPUT_DIR/coverage.xml --cov-report=term | tee $OUTPUT_DIR/pytest_output.txt

# linter実行
poetry run ruff check youtube_transcript_api | tee $OUTPUT_DIR/ruff_output.txt

# フォーマットチェック
poetry run ruff format youtube_transcript_api --check | tee $OUTPUT_DIR/format_check.txt

# 結果のサマリー作成
echo "=== Test Summary ===" > $OUTPUT_DIR/summary.txt
echo "Date: $(date)" >> $OUTPUT_DIR/summary.txt
echo "Git commit: $(git rev-parse HEAD)" >> $OUTPUT_DIR/summary.txt
echo "" >> $OUTPUT_DIR/summary.txt
echo "PyTest results:" >> $OUTPUT_DIR/summary.txt
tail -n 20 $OUTPUT_DIR/pytest_output.txt | grep -E "(passed|failed|error)" >> $OUTPUT_DIR/summary.txt || true

echo "Baseline tests completed. Results saved to $OUTPUT_DIR"
