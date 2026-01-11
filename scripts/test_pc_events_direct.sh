#!/bin/bash
# Test Planning Center API directly to see events and find oldest by created_at

echo "═══════════════════════════════════════════════════════════════"
echo "Planning Center API - Direct Events Test"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check if credentials are provided
if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <APP_ID> <SECRET>"
    echo ""
    echo "Or load from environment:"
    echo "  export PLANNING_CENTER_APP_ID=your_app_id"
    echo "  export PLANNING_CENTER_SECRET=your_secret"
    echo "  $0"
    echo ""
    exit 1
fi

APP_ID=${1:-$PLANNING_CENTER_APP_ID}
SECRET=${2:-$PLANNING_CENTER_SECRET}

if [ -z "$APP_ID" ] || [ -z "$SECRET" ]; then
    echo "❌ Error: APP_ID and SECRET required"
    exit 1
fi

echo "Testing Planning Center API..."
echo ""

# Test Check-Ins API first
echo "1️⃣  Testing Check-Ins API (sorted by created_at, newest first)..."
echo ""

CHECKINS_RESPONSE=$(curl -s -u "$APP_ID:$SECRET" \
    "https://api.planningcenteronline.com/check-ins/v2/events?per_page=10&offset=0&order=-created_at")

# Check if Check-Ins API is available
if echo "$CHECKINS_RESPONSE" | grep -q '"data"'; then
    echo "✅ Check-Ins API accessible"
    
    # Get first event (newest)
    FIRST_EVENT=$(echo "$CHECKINS_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    events = data.get('data', [])
    if events:
        print(json.dumps(events[0], indent=2))
except:
    pass
" 2>/dev/null)
    
    if [ -n "$FIRST_EVENT" ]; then
        echo ""
        echo "📅 First event (newest created_at):"
        echo "$FIRST_EVENT" | python3 -c "
import sys, json
event = json.load(sys.stdin)
attrs = event.get('attributes', {})
print(f\"  ID: {event.get('id')}\")
print(f\"  Name: {attrs.get('name')}\")
print(f\"  Created at: {attrs.get('created_at')}\")
print(f\"  Start date: {attrs.get('start_date')}\")
" 2>/dev/null
    fi
    
    # Get last event (oldest)
    TOTAL=$(echo "$CHECKINS_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    events = data.get('data', [])
    print(len(events))
except:
    print(0)
" 2>/dev/null)
    
    if [ "$TOTAL" -gt 0 ]; then
        LAST_EVENT=$(echo "$CHECKINS_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    events = data.get('data', [])
    if events:
        print(json.dumps(events[-1], indent=2))
except:
    pass
" 2>/dev/null)
        
        echo ""
        echo "📅 Last event in response (oldest created_at in this page):"
        echo "$LAST_EVENT" | python3 -c "
import sys, json
event = json.load(sys.stdin)
attrs = event.get('attributes', {})
print(f\"  ID: {event.get('id')}\")
print(f\"  Name: {attrs.get('name')}\")
print(f\"  Created at: {attrs.get('created_at')}\")
print(f\"  Start date: {attrs.get('start_date')}\")
" 2>/dev/null
    fi
else
    echo "❌ Check-Ins API not accessible or returned error"
    echo "Response: $(echo "$CHECKINS_RESPONSE" | head -5)"
    echo ""
fi

echo ""
echo "2️⃣  Testing Calendar API (sorted by starts_at, newest first)..."
echo ""

CALENDAR_RESPONSE=$(curl -s -u "$APP_ID:$SECRET" \
    "https://api.planningcenteronline.com/calendar/v2/events?per_page=10&offset=0&order=-starts_at")

# Check if Calendar API is available
if echo "$CALENDAR_RESPONSE" | grep -q '"data"'; then
    echo "✅ Calendar API accessible"
    
    # Get first event (newest)
    FIRST_EVENT=$(echo "$CALENDAR_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    events = data.get('data', [])
    if events:
        print(json.dumps(events[0], indent=2))
except:
    pass
" 2>/dev/null)
    
    if [ -n "$FIRST_EVENT" ]; then
        echo ""
        echo "📅 First event (newest starts_at):"
        echo "$FIRST_EVENT" | python3 -c "
import sys, json
event = json.load(sys.stdin)
attrs = event.get('attributes', {})
print(f\"  ID: {event.get('id')}\")
print(f\"  Name: {attrs.get('name')}\")
print(f\"  Starts at: {attrs.get('starts_at')}\")
" 2>/dev/null
    fi
    
    # Get last event (oldest)
    TOTAL=$(echo "$CALENDAR_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    events = data.get('data', [])
    print(len(events))
except:
    print(0)
" 2>/dev/null)
    
    if [ "$TOTAL" -gt 0 ]; then
        LAST_EVENT=$(echo "$CALENDAR_RESPONSE" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    events = data.get('data', [])
    if events:
        print(json.dumps(events[-1], indent=2))
except:
    pass
" 2>/dev/null)
        
        echo ""
        echo "📅 Last event in response (oldest starts_at in this page):"
        echo "$LAST_EVENT" | python3 -c "
import sys, json
event = json.load(sys.stdin)
attrs = event.get('attributes', {})
print(f\"  ID: {event.get('id')}\")
print(f\"  Name: {attrs.get('name')}\")
print(f\"  Starts at: {attrs.get('starts_at')}\")
" 2>/dev/null
    fi
else
    echo "❌ Calendar API not accessible or returned error"
    echo "Response: $(echo "$CALENDAR_RESPONSE" | head -5)"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "To find the oldest event with 1000 limit, check offset 990:"
echo "  curl -u \"$APP_ID:$SECRET\" \\"
echo "    \"https://api.planningcenteronline.com/calendar/v2/events?per_page=10&offset=990&order=-starts_at\""
echo "═══════════════════════════════════════════════════════════════"



