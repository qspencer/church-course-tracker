#!/bin/bash
# Quick test script for Planning Center integration

echo "🧪 Planning Center Integration - Quick Test"
echo "============================================"
echo ""

# Check if server is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
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

# Test 1: Connection test
echo "Test 1: Connection Test"
echo "-----------------------"
curl -s http://localhost:8000/api/v1/planning-center/test-connection | python3 -m json.tool
echo ""
echo ""

# Test 2: Sync people
echo "Test 2: Sync People (Background Task)"
echo "--------------------------------------"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/planning-center/people)
echo "$RESPONSE" | python3 -m json.tool
echo ""

# Extract task_id if available
TASK_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('task_id', ''))" 2>/dev/null)

if [ -n "$TASK_ID" ]; then
    echo "Task ID: $TASK_ID"
    echo ""
    echo "Test 3: Check Task Status"
    echo "-------------------------"
    sleep 2
    curl -s http://localhost:8000/api/v1/planning-center/tasks/$TASK_ID | python3 -m json.tool
    echo ""
    echo ""
fi

# Test 4: List all tasks
echo "Test 4: List All Tasks"
echo "----------------------"
curl -s http://localhost:8000/api/v1/planning-center/tasks | python3 -m json.tool
echo ""
echo ""

echo "✅ Quick test complete!"
echo ""
echo "📝 Note: Sync tasks run in the background. Check task status to see progress."

