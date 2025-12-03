#!/bin/bash
# Simple auth test

API="http://54.251.65.124/api"

echo "=== Auth Test ==="
echo ""

# Test 1: Health
echo "1. Health Check"
curl -s $API/health | jq -r '.status' && echo "✅ Backend running" || echo "❌ Backend down"
echo ""

# Test 2: Login
echo "2. Login Test"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST $API/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@agridao.com","password":"admin123"}')

STATUS=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$STATUS" = "200" ]; then
    echo "✅ Login successful"
    TOKEN=$(echo "$BODY" | jq -r '.access_token')
    echo "Token: ${TOKEN:0:30}..."
    
    # Test 3: Authenticated request
    echo ""
    echo "3. Authenticated Request"
    AUTH_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET $API/auth/me \
        -H "Authorization: Bearer $TOKEN")
    
    AUTH_STATUS=$(echo "$AUTH_RESPONSE" | tail -n1)
    
    if [ "$AUTH_STATUS" = "200" ]; then
        echo "✅ Auth working correctly"
        echo "$AUTH_RESPONSE" | sed '$d' | jq .
    else
        echo "❌ Auth failed (Status: $AUTH_STATUS)"
    fi
else
    echo "❌ Login failed (Status: $STATUS)"
    echo "$BODY" | jq .
fi
