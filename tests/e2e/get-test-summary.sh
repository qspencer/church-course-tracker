#!/bin/bash

# Quick Test Summary - Provides summary from available data or runs a sample

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "E2E Test Suite Summary"
echo "=========================================="
echo ""

# Get total test count
TOTAL_TESTS=$(npx playwright test --list --project=chromium 2>&1 | grep -c "\[chromium\]" || echo "0")
echo "Total Tests: $TOTAL_TESTS"
echo ""

# Check if we have any results
if [ -f test-results/results.json ]; then
    echo "Parsing results from test-results/results.json..."
    python3 << 'PYTHON_SCRIPT'
import json
import sys

try:
    with open('test-results/results.json', 'r') as f:
        content = f.read().strip()
        # Try to find the last JSON object
        lines = content.split('\n')
        for line in reversed(lines):
            line = line.strip()
            if line and line.startswith('{'):
                try:
                    data = json.loads(line)
                    if 'stats' in data:
                        stats = data['stats']
                        print(f"Passed:   {stats.get('passed', 0)}")
                        print(f"Failed:   {stats.get('failed', 0)}")
                        print(f"Skipped:  {stats.get('skipped', 0)}")
                        total = stats.get('total', 0)
                        if total > 0:
                            rate = (stats.get('passed', 0) / total) * 100
                            print(f"Success Rate: {rate:.1f}%")
                        sys.exit(0)
                except:
                    continue
    print("Could not parse results.json")
except Exception as e:
    print(f"Error: {e}")
PYTHON_SCRIPT
else
    echo "No results file found."
    echo ""
    echo "To get complete results, run:"
    echo "  ./run-tests-summary.sh"
    echo ""
    echo "Or run tests in batches:"
    echo "  ./run-tests-batch.sh"
fi

echo ""
echo "=========================================="
