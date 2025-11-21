#!/bin/bash
# Quick test script for the documentation server

echo "🧪 Testing Documentation Server..."
echo ""

# Test 1: Check if server is running
echo "1. Checking if server is running..."
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8000 | grep -q "200\|302"; then
    echo "   ✅ Server is responding"
else
    echo "   ❌ Server is not responding"
    exit 1
fi

# Test 2: Get server response
echo ""
echo "2. Testing server response..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -L http://127.0.0.1:8000)
echo "   HTTP Status: $HTTP_CODE"

# Test 3: Check page title
echo ""
echo "3. Checking page content..."
TITLE=$(curl -s -L http://127.0.0.1:8000 | grep -o '<title>[^<]*</title>' | head -1)
if [ -n "$TITLE" ]; then
    echo "   ✅ Page title found: $TITLE"
else
    echo "   ⚠️  Could not find page title"
fi

# Test 4: Check port
echo ""
echo "4. Checking port 8000..."
if lsof -i :8000 > /dev/null 2>&1 || ss -tuln | grep -q ":8000"; then
    echo "   ✅ Port 8000 is listening"
else
    echo "   ❌ Port 8000 is not listening"
fi

echo ""
echo "✅ Server test complete!"
echo ""
echo "📝 To access from your local browser:"
echo "   1. Set up SSH port forwarding:"
echo "      ssh -L 8000:localhost:8000 ubuntu@<server-ip>"
echo "   2. Then open: http://localhost:8000"
echo ""

