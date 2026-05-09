#!/bin/bash

# Verify that version.txt, environment.ts, and environment.prod.ts all agree
# on the same version string. Exits non-zero if they don't, with a clear diff.
# Wire this into CI (or a pre-commit hook) to prevent the drift bug we hit
# in May 2026 where three files held three different versions.

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION_FILE="$PROJECT_ROOT/frontend/church-course-tracker/version.txt"
ENV_BASE_FILE="$PROJECT_ROOT/frontend/church-course-tracker/src/environments/environment.ts"
ENV_PROD_FILE="$PROJECT_ROOT/frontend/church-course-tracker/src/environments/environment.prod.ts"

extract_env_version() {
    grep -oE "version: *['\"][^'\"]+['\"]" "$1" \
        | head -n1 \
        | sed -E "s/version: *['\"]([^'\"]+)['\"]/\1/"
}

VER_TXT=$(tr -d '[:space:]' < "$VERSION_FILE" 2>/dev/null || echo "")
VER_BASE=$(extract_env_version "$ENV_BASE_FILE" 2>/dev/null || echo "")
VER_PROD=$(extract_env_version "$ENV_PROD_FILE" 2>/dev/null || echo "")

if [ -z "$VER_TXT" ] || [ -z "$VER_BASE" ] || [ -z "$VER_PROD" ]; then
    echo "❌ Could not extract a version from one or more files." >&2
    echo "   version.txt:        '$VER_TXT'" >&2
    echo "   environment.ts:     '$VER_BASE'" >&2
    echo "   environment.prod.ts:'$VER_PROD'" >&2
    exit 1
fi

if [ "$VER_TXT" = "$VER_BASE" ] && [ "$VER_BASE" = "$VER_PROD" ]; then
    echo "✅ All three sources agree: $VER_TXT"
    exit 0
fi

echo "❌ Version drift detected:" >&2
echo "   version.txt:        $VER_TXT" >&2
echo "   environment.ts:     $VER_BASE" >&2
echo "   environment.prod.ts:$VER_PROD" >&2
echo "" >&2
echo "Run scripts/increment-version.sh, or hand-edit all three to match." >&2
exit 1
