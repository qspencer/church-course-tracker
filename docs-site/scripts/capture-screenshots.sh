#!/bin/bash
# Script to capture screenshots for documentation

set -e

echo "📸 Capturing screenshots for documentation..."
echo ""

cd "$(dirname "$0")/.."

# Check if Node.js and Playwright are available
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    exit 1
fi

# Check if Playwright is installed
if [ ! -d "../node_modules/@playwright" ]; then
    echo "📦 Installing Playwright..."
    cd ..
    npm install @playwright/test
    npx playwright install chromium
    cd docs-site
fi

# Compile TypeScript if needed
if [ ! -f "scripts/capture-screenshots.js" ] || [ "scripts/capture-screenshots.ts" -nt "scripts/capture-screenshots.js" ]; then
    echo "🔨 Compiling TypeScript..."
    npx tsc scripts/capture-screenshots.ts --esModuleInterop --module commonjs --target es2020 --outDir scripts
fi

# Run the screenshot script
echo "🚀 Running screenshot capture..."
node scripts/capture-screenshots.js

echo ""
echo "✅ Screenshot capture complete!"
echo ""
echo "📁 Screenshots saved to: docs-site/docs/images/screenshots/"

