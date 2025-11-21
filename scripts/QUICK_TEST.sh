#!/bin/bash
# Quick test script for Planning Center integration

echo "🧪 Planning Center Integration - Quick Test"
echo "============================================"
echo ""

# Check if server is running
if ! curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "⚠️  Backend server not running!"
    echo ""
    echo "Please start the server first:"
    echo "  cd backend"
    echo "  source venv_new/bin/activate"
    echo "  export DATABASE_URL=\"sqlite:///./data/church_course_tracker.db\""
    echo "  uvicorn main:app --reload"
    echo ""
    exit 1
fi

echo "✅ Backend server is running"
echo ""

# Helper function to safely parse JSON
safe_json() {
    local response="$1"
    if python3 -c "import json, sys; json.loads('$response')" 2>/dev/null; then
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
    else
        echo "$response"
    fi
}

# Test 1: Connection test
echo "Test 1: Connection Test"
echo "-----------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" http://localhost:8000/api/v1/planning-center/test-connection)
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "200" ]; then
    safe_json "$BODY"
else
    echo "❌ HTTP $HTTP_CODE"
    echo "$BODY"
fi
echo ""
echo ""

# Test 2: Sync people
echo "Test 2: Sync People (Background Task)"
echo "--------------------------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" -X POST http://localhost:8000/api/v1/planning-center/people)
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "200" ]; then
    safe_json "$BODY"
    # Extract task_id if available
    TASK_ID=$(echo "$BODY" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('task_id', ''))" 2>/dev/null)
    
    if [ -n "$TASK_ID" ] && [ "$TASK_ID" != "None" ]; then
        echo ""
        echo "Task ID: $TASK_ID"
        echo ""
        echo "Test 3: Check Task Status (after 2 seconds)"
        echo "-------------------------"
        sleep 2
        TASK_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "http://localhost:8000/api/v1/planning-center/tasks/$TASK_ID")
        TASK_HTTP_CODE=$(echo "$TASK_RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
        TASK_BODY=$(echo "$TASK_RESPONSE" | sed '/HTTP_CODE/d')
        if [ "$TASK_HTTP_CODE" = "200" ]; then
            safe_json "$TASK_BODY"
        else
            echo "❌ HTTP $TASK_HTTP_CODE"
            echo "$TASK_BODY"
        fi
        echo ""
    fi
else
    echo "❌ HTTP $HTTP_CODE"
    echo "$BODY"
fi
echo ""
echo ""

# Test 4: List all tasks
echo "Test 4: List All Tasks"
echo "----------------------"
RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" http://localhost:8000/api/v1/planning-center/tasks)
HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | sed '/HTTP_CODE/d')

if [ "$HTTP_CODE" = "200" ]; then
    safe_json "$BODY"
else
    echo "❌ HTTP $HTTP_CODE"
    echo "$BODY"
fi
echo ""
echo ""

echo "✅ Quick test complete!"
echo ""
echo "📝 Note: Sync tasks run in the background. Check task status to see progress."

