#!/bin/bash
# Search for a specific event in Planning Center API

SEARCH_TERM="${1:-Practicing the Way}"

# Load credentials from backend/.env if they exist
if [ -f "backend/.env" ]; then
    export $(grep -E "^PLANNING_CENTER_APP_ID=|^PLANNING_CENTER_SECRET=" backend/.env | grep -v '^#' | xargs)
fi

APP_ID=${PLANNING_CENTER_APP_ID}
SECRET=${PLANNING_CENTER_SECRET}

if [ -z "$APP_ID" ] || [ -z "$SECRET" ]; then
    echo "❌ Error: PLANNING_CENTER_APP_ID and PLANNING_CENTER_SECRET must be set"
    exit 1
fi

echo "═══════════════════════════════════════════════════════════════"
echo "Searching Planning Center for: '$SEARCH_TERM'"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Create a Python script to search
cat > /tmp/pc_search.py << 'PYEOF'
import sys
import json

search_term = sys.argv[1].lower()
file_path = sys.argv[2]

try:
    with open(file_path, 'r') as f:
        data = json.load(f)
    events = data.get('data', [])
    
    matches = []
    
    for event in events:
        attrs = event.get('attributes', {})
        name = attrs.get('name', '')
        
        if search_term in name.lower():
            matches.append({
                'id': event.get('id'),
                'name': name,
                'created_at': attrs.get('created_at'),
                'starts_at': attrs.get('starts_at'),
                'description': (attrs.get('description', '')[:100]) if attrs.get('description') else None
            })
    
    if matches:
        print(json.dumps(matches, indent=2))
    else:
        print("[]")
        
except Exception as e:
    print(f'{{"error": "{str(e)}"}}')
PYEOF

# Search through events in batches
FOUND=0
OFFSET=0
PER_PAGE=100
MAX_SEARCH=2000  # Search up to 2000 events

echo "Searching through events..."
echo ""

while [ $OFFSET -lt $MAX_SEARCH ]; do
    # Fetch events from Calendar API to temp file
    TMPFILE="/tmp/pc_search_${OFFSET}.json"
    curl -s -u "$APP_ID:$SECRET" \
        "https://api.planningcenteronline.com/calendar/v2/events?per_page=$PER_PAGE&offset=$OFFSET&order=-starts_at" > "$TMPFILE"
    
    # Check for errors
    if grep -q '"errors"' "$TMPFILE"; then
        echo "Error from API at offset $OFFSET:"
        python3 -m json.tool "$TMPFILE" 2>/dev/null | head -5
        rm -f "$TMPFILE"
        break
    fi
    
    # Search in the response
    RESULTS=$(python3 /tmp/pc_search.py "$SEARCH_TERM" "$TMPFILE" 2>/dev/null)
    
    # Check event count before deleting
    EVENT_COUNT=$(python3 -c "import json; f=open('$TMPFILE', 'r'); d=json.load(f); print(len(d.get('data', []))); f.close()" 2>/dev/null || echo "0")
    
    rm -f "$TMPFILE"
    
    # Check if we have actual results
    if [ "$RESULTS" != "[]" ] && [ "$RESULTS" != "" ] && ! echo "$RESULTS" | grep -q '"error"'; then
        echo "✅ Found matches in events $OFFSET-$((OFFSET+PER_PAGE-1)):"
        echo "$RESULTS" | python3 -m json.tool
        echo ""
        FOUND=1
    fi
    
    # Check if we've reached the end
    if [ "$EVENT_COUNT" -lt "$PER_PAGE" ]; then
        break
    fi
    
    OFFSET=$((OFFSET + PER_PAGE))
    
    # Progress indicator
    if [ $((OFFSET % 500)) -eq 0 ]; then
        echo "  Searched $OFFSET events..."
    fi
done

rm -f /tmp/pc_search.py

if [ $FOUND -eq 0 ]; then
    echo "❌ No events found matching '$SEARCH_TERM'"
    echo ""
    echo "Searched through $OFFSET events."
    echo "Try a different search term or check if the event exists in Planning Center."
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
