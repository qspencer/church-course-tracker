#!/bin/bash
# Helper script to test the Planning Center events diagnostics endpoint

echo "═══════════════════════════════════════════════════════════════"
echo "Planning Center Events Diagnostic Endpoint Test"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check if token is provided as argument
if [ -n "$1" ]; then
    TOKEN=$1
    echo "Using provided token..."
else
    echo "No token provided. Attempting to get token from login..."
    echo ""
    
    # Try to login (user will need to provide password)
    read -p "Enter username [Admin]: " USERNAME
    USERNAME=${USERNAME:-Admin}
    read -sp "Enter password: " PASSWORD
    echo ""
    
    echo "Logging in..."
    LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
        -H "Content-Type: application/json" \
        -d "{\"username\": \"$USERNAME\", \"password\": \"$PASSWORD\"}")
    
    # Check if login was successful
    if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
        TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
        if [ -z "$TOKEN" ]; then
            echo "❌ Could not extract token from login response"
            echo "Response: $LOGIN_RESPONSE"
            exit 1
        fi
        echo "✅ Login successful!"
    else
        echo "❌ Login failed"
        echo "Response: $LOGIN_RESPONSE"
        exit 1
    fi
fi

echo ""
echo "Fetching diagnostic information..."
echo ""

# Call the diagnostic endpoint
RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
    http://localhost:8000/api/v1/planning-center/events/diagnostics)

# Check if request was successful
if echo "$RESPONSE" | grep -q "total_events"; then
    echo "✅ Diagnostic data retrieved successfully!"
    echo ""
    echo "$RESPONSE" | python3 -m json.tool
else
    echo "❌ Request failed"
    echo "Response: $RESPONSE"
    exit 1
fi



