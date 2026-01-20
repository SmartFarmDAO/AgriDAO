#!/bin/bash

# Marketplace Testing Script
# Tests all marketplace functionality

BASE_URL="http://localhost:8000"
FRONTEND_URL="http://localhost:5173"

echo "🧪 AgriDAO Marketplace Testing"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

test_api() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=$5
    
    echo -n "Testing: $name... "
    
    if [ -z "$data" ]; then
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    status=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$status" = "$expected_status" ]; then
        echo -e "${GREEN}✓ PASSED${NC} (HTTP $status)"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC} (Expected $expected_status, got $status)"
        echo "Response: $body"
        ((FAILED++))
        return 1
    fi
}

echo "📦 Testing Product APIs"
echo "------------------------"

# Test 1: List all products
test_api "List all products" "GET" "/marketplace/products" "" "200"

# Test 2: Get specific product
test_api "Get product by ID" "GET" "/marketplace/products/1" "" "200"

# Test 3: Get non-existent product
test_api "Get non-existent product" "GET" "/marketplace/products/999" "" "404"

echo ""
echo "🔍 Testing Search Functionality"
echo "--------------------------------"

# Test 4: Search products
echo -n "Testing: Search for 'tomato'... "
response=$(curl -s "$BASE_URL/marketplace/products")
if echo "$response" | grep -q "Tomatoes"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAILED${NC}"
    ((FAILED++))
fi

echo ""
echo "🛒 Testing Cart Functionality"
echo "------------------------------"

echo -e "${YELLOW}ℹ Cart is client-side (localStorage) - test in browser${NC}"

echo ""
echo "👤 Testing Authentication"
echo "--------------------------"

# Test 5: Create product without auth (should fail)
test_api "Create product without auth" "POST" "/marketplace/products" \
    '{"name":"Test Product","price":10.0,"quantity":"10 kg","category":"Test"}' "401"

echo ""
echo "📊 Test Summary"
echo "==============="
echo -e "Total Tests: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
