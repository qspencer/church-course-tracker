#!/bin/bash

# Quick Test Summary Script
# Runs tests and provides a concise summary

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Configuration
WORKERS=${WORKERS:-2}
TIMEOUT=${TIMEOUT:-1800}  # 30 minutes total
RESULTS_FILE="test-results/summary.txt"

mkdir -p test-results

echo "Running E2E tests and generating summary..."
echo "This may take a while..."
echo ""

# Run tests with JSON reporter for easier parsing
timeout $TIMEOUT npx playwright test --project=chromium --workers=$WORKERS --reporter=json --output=test-results/results.json > test-results/test-output.log 2>&1 || true

# Parse and display summary
if [ -f test-results/results.json ]; then
    python3 << 'PYTHON_SCRIPT'
import json
import sys

try:
    with open('test-results/results.json', 'r') as f:
        # Read the last line which should be the JSON summary
        lines = f.readlines()
        if not lines:
            print("No results found in results.json")
            sys.exit(1)
        
        # Try to parse the last line as JSON
        last_line = lines[-1].strip()
        try:
            data = json.loads(last_line)
        except json.JSONDecodeError:
            # If last line is not JSON, try to find JSON in the file
            for line in reversed(lines):
                line = line.strip()
                if line.startswith('{') and line.endswith('}'):
                    try:
                        data = json.loads(line)
                        break
                    except json.JSONDecodeError:
                        continue
            else:
                print("Could not parse JSON from results.json")
                sys.exit(1)
        
        stats = data.get('stats', {})
        total = stats.get('total', 0)
        passed = stats.get('passed', 0)
        failed = stats.get('failed', 0)
        skipped = stats.get('skipped', 0)
        
        print("=" * 50)
        print("E2E Test Results Summary")
        print("=" * 50)
        print(f"Total Tests:  {total}")
        print(f"Passed:       {passed}")
        print(f"Failed:       {failed}")
        print(f"Skipped:      {skipped}")
        
        if total > 0:
            success_rate = (passed / total) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        
        print("=" * 50)
        
        # List failed tests if any
        if failed > 0:
            print("\nFailed Tests:")
            print("-" * 50)
            for suite in data.get('suites', []):
                for spec in suite.get('specs', []):
                    for test in spec.get('tests', []):
                        if test.get('results', [{}])[0].get('status') == 'failed':
                            title = test.get('title', 'Unknown')
                            file = spec.get('file', 'Unknown')
                            print(f"  ✘ {title}")
                            print(f"    File: {file}")
        
        # List skipped tests if any
        if skipped > 0:
            print(f"\nSkipped Tests: {skipped} (see test output for details)")
        
except FileNotFoundError:
    print("Results file not found. Tests may have timed out or failed to run.")
    sys.exit(1)
except Exception as e:
    print(f"Error parsing results: {e}")
    sys.exit(1)
PYTHON_SCRIPT
else
    echo "Results file not found. Tests may have timed out."
    echo "Check test-results/test-output.log for details."
    exit 1
fi
