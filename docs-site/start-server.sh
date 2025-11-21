#!/bin/bash
# Start the MkDocs development server

cd "$(dirname "$0")"

echo "🚀 Starting Church Course Tracker Documentation Server..."
echo ""

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating it..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

echo "📚 Starting MkDocs server..."
echo "📍 Server will be available at:"
echo "   - http://localhost:8000 (local access)"
echo "   - http://127.0.0.1:8000 (local access)"
echo ""
echo "💡 If accessing remotely, use SSH port forwarding:"
echo "   ssh -L 8000:localhost:8000 user@server"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the server with dev config (no path prefix)
mkdocs serve --dev-addr=0.0.0.0:8000 --config-file=mkdocs.dev.yml

