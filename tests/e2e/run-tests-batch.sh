#!/bin/bash

# Batch Test Runner for E2E Tests
# This script runs tests in smaller batches to avoid timeouts and collects complete results

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
WORKERS=${WORKERS:-2}
TIMEOUT_PER_BATCH=${TIMEOUT_PER_BATCH:-600}  # 10 minutes per batch
RESULTS_DIR="test-results"
SUMMARY_FILE="$RESULTS_DIR/test-summary.json"
LOG_FILE="$RESULTS_DIR/batch-run.log"

# Create results directory
mkdir -p "$RESULTS_DIR"

# Initialize summary if it doesn't exist
if [ ! -f "$SUMMARY_FILE" ]; then
    echo '{"total": 0, "passed": 0, "failed": 0, "skipped": 0, "batches": []}' > "$SUMMARY_FILE"
fi

# Get all test files
TEST_FILES=$(npx playwright test --list --project=chromium 2>&1 | grep -E "\.spec\.ts:" | sed 's/.*\[chromium\] › //' | sed 's/:.*//' | sort -u)

# Count total tests
TOTAL_TESTS=$(npx playwright test --list --project=chromium 2>&1 | grep -c "\[chromium\]" || echo "0")

echo "=========================================="
echo "E2E Test Batch Runner"
echo "=========================================="
echo "Total test files: $(echo "$TEST_FILES" | wc -l)"
echo "Total tests: $TOTAL_TESTS"
echo "Workers: $WORKERS"
echo "Timeout per batch: ${TIMEOUT_PER_BATCH}s"
echo "=========================================="
echo ""

# Function to update summary
update_summary() {
    local batch_file=$1
    local batch_passed=$2
    local batch_failed=$3
    local batch_skipped=$4
    
    python3 << EOF
import json
import sys
import os

# Initialize summary if file doesn't exist
if not os.path.exists('$SUMMARY_FILE'):
    summary = {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "batches": []}
else:
    with open('$SUMMARY_FILE', 'r') as f:
        summary = json.load(f)

summary['total'] += ($batch_passed + $batch_failed + $batch_skipped)
summary['passed'] += $batch_passed
summary['failed'] += $batch_failed
summary['skipped'] += $batch_skipped
summary['batches'].append({
    'file': '$batch_file',
    'passed': $batch_passed,
    'failed': $batch_failed,
    'skipped': $batch_skipped
})

with open('$SUMMARY_FILE', 'w') as f:
    json.dump(summary, f, indent=2)
EOF
}

# Function to parse test results
parse_results() {
    local output_file=$1
    local passed=$(grep -c "✓" "$output_file" 2>/dev/null || echo "0")
    local failed=$(grep -c "✘" "$output_file" 2>/dev/null || echo "0")
    local skipped=$(grep -c "^\s*-" "$output_file" 2>/dev/null || echo "0")
    echo "$passed $failed $skipped"
}

# Run tests in batches
BATCH_NUM=1
for test_file in $TEST_FILES; do
    echo "[Batch $BATCH_NUM] Running: $test_file"
    echo "----------------------------------------"
    
    BATCH_OUTPUT="$RESULTS_DIR/batch-${BATCH_NUM}-$(basename $test_file .spec.ts).log"
    
    # Run the test file with timeout
    if timeout $TIMEOUT_PER_BATCH npx playwright test "$test_file" --project=chromium --workers=$WORKERS --reporter=list > "$BATCH_OUTPUT" 2>&1; then
        # Parse results
        read passed failed skipped <<< $(parse_results "$BATCH_OUTPUT")
        update_summary "$test_file" "$passed" "$failed" "$skipped"
        
        echo -e "${GREEN}✓${NC} Passed: $passed, Failed: $failed, Skipped: $skipped"
    else
        EXIT_CODE=$?
        if [ $EXIT_CODE -eq 124 ]; then
            echo -e "${YELLOW}⚠${NC} Batch timed out after ${TIMEOUT_PER_BATCH}s"
            read passed failed skipped <<< $(parse_results "$BATCH_OUTPUT")
            update_summary "$test_file" "$passed" "$failed" "$skipped"
        else
            echo -e "${RED}✘${NC} Batch failed with exit code $EXIT_CODE"
            read passed failed skipped <<< $(parse_results "$BATCH_OUTPUT")
            update_summary "$test_file" "$passed" "$failed" "$skipped"
        fi
    fi
    
    echo ""
    BATCH_NUM=$((BATCH_NUM + 1))
done

# Print final summary
echo "=========================================="
echo "Final Summary"
echo "=========================================="

python3 << EOF
import json

with open('$SUMMARY_FILE', 'r') as f:
    summary = json.load(f)

print(f"Total Tests: {summary['total']}")
print(f"Passed: {summary['passed']}")
print(f"Failed: {summary['failed']}")
print(f"Skipped: {summary['skipped']}")
print(f"Success Rate: {(summary['passed'] / summary['total'] * 100) if summary['total'] > 0 else 0:.1f}%")
EOF

echo ""
echo "Detailed results saved to: $SUMMARY_FILE"
echo "Batch logs saved to: $RESULTS_DIR/batch-*.log"
