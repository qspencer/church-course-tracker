#!/bin/bash
# Quick test to find the oldest event returned by Planning Center API with 1000 limit

# Load credentials from backend/.env if they exist
if [ -f "backend/.env" ]; then
    export $(grep -E "^PLANNING_CENTER_APP_ID=|^PLANNING_CENTER_SECRET=" backend/.env | grep -v '^#' | xargs)
fi

# Use provided credentials or environment variables
APP_ID=${1:-$PLANNING_CENTER_APP_ID}
SECRET=${2:-$PLANNING_CENTER_SECRET}

if [ -z "$APP_ID" ] || [ -z "$SECRET" ]; then
    echo "❌ Error: APP_ID and SECRET required"
    echo ""
    echo "Usage:"
    echo "  $0 [APP_ID] [SECRET]"
    echo ""
    echo "Or set environment variables:"
    echo "  export PLANNING_CENTER_APP_ID=your_id"
    echo "  export PLANNING_CENTER_SECRET=your_secret"
    echo "  $0"
    exit 1
fi

echo "═══════════════════════════════════════════════════════════════"
echo "Finding oldest event in Planning Center API (with 1000 limit)"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Test Calendar API first (since that's what we're using)
echo "Testing Calendar API - fetching last 10 events (offset 990-999)..."
echo ""

RESPONSE=$(curl -s -u "$APP_ID:$SECRET" \
    "https://api.planningcenteronline.com/calendar/v2/events?per_page=10&offset=990&order=-starts_at")

# Check for errors
if echo "$RESPONSE" | grep -q '"errors"'; then
    echo "❌ Error from Planning Center API:"
    echo "$RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$RESPONSE"
    exit 1
fi

# Parse the response to find oldest event
OLDEST=$(echo "$RESPONSE" | python3 << 'PYEOF'
import sys, json
from datetime import datetime

try:
    data = json.load(sys.stdin)
    events = data.get('data', [])
    
    if not events:
        print("No events found")
        sys.exit(0)
    
    # Events are sorted by starts_at descending, so last is oldest
    oldest = events[-1]
    attrs = oldest.get('attributes', {})
    
    print(f"✅ Found {len(events)} events in this page")
    print("")
    print("📅 Oldest event (last in sorted list, offset 990-999):")
    print(f"  ID: {oldest.get('id')}")
    print(f"  Name: {attrs.get('name', 'N/A')}")
    print(f"  Starts at: {attrs.get('starts_at', 'N/A')}")
    print("")
    
    # Also show the first event (newest)
    newest = events[0]
    newest_attrs = newest.get('attributes', {})
    print("📅 Newest event in this page:")
    print(f"  ID: {newest.get('id')}")
    print(f"  Name: {newest_attrs.get('name', 'N/A')}")
    print(f"  Starts at: {newest_attrs.get('starts_at', 'N/A')}")
    
except Exception as e:
    print(f"Error parsing response: {e}")
    sys.exit(1)
PYEOF
)

echo "$OLDEST"

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "To see all events in this range, run:"
echo "  curl -u \"$APP_ID:$SECRET\" \\"
echo "    \"https://api.planningcenteronline.com/calendar/v2/events?per_page=10&offset=990&order=-starts_at\" \\"
echo "    | python3 -m json.tool"
echo "═══════════════════════════════════════════════════════════════"



