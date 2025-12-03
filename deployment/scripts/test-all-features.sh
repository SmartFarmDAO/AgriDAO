#!/bin/bash

# AgriDAO Comprehensive Feature Testing Script
# Tests all major features and generates a detailed report

set -e

# Configuration
API_URL="${API_URL:-http://54.251.65.124/api}"
RESULTS_DIR="./test-results"
TIMESTAMP=$(date +%Y%m%d-%H%M%S)
RESULTS_FILE="$RESULTS_DIR/test-results-$TIMESTAMP.txt"
JSON_FILE="$RESULTS_DIR/test-results-$TIMESTAMP.json"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create results directory
mkdir -p $RESULTS_DIR

# Initialize results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Helper functions
log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1" | tee -a $RESULTS_FILE
}

error() {
    echo -e "${RED}[$(date +'%H:%M:%S')] ERROR:${NC} $1" | tee -a $RESULTS_FILE
}

warn() {
    echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING:${NC} $1" | tee -a $RESULTS_FILE
}

test_api() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=$5
    local auth_token=$6
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    log "Testing: $name"
    
    local headers="-H 'Content-Type: application/json'"
    if [ -n "$auth_token" ]; then
        headers="$headers -H 'Authorization: Bearer $auth_token'"
    fi
    
    local cmd="curl -s -w '\n%{http_code}' -X $method $API_URL$endpoint $headers"
    if [ -n "$data" ]; then
        cmd="$cmd -d '$data'"
    fi
    
    local response=$(eval $cmd)
    local status_code=$(echo "$response" | tail -n1)
    local body=$(echo "$response" | sed '$d')
    
    echo "  Request: $method $endpoint" >> $RESULTS_FILE
    echo "  Status: $status_code (Expected: $expected_status)" >> $RESULTS_FILE
    echo "  Response: $body" >> $RESULTS_FILE
    echo "" >> $RESULTS_FILE
    
    if [ "$status_code" = "$expected_status" ]; then
        echo -e "  ${GREEN}✓ PASSED${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "  ${RED}✗ FAILED${NC} (Got $status_code, expected $expected_status)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Start testing
log "=== AgriDAO Feature Testing ==="
log "API URL: $API_URL"
log "Timestamp: $TIMESTAMP"
echo "" | tee -a $RESULTS_FILE

# Phase 1: Health Checks
log "Phase 1: Health Checks"
test_api "Health Check" "GET" "/health" "" "200"
test_api "Database Health" "GET" "/health/db" "" "200"
echo "" | tee -a $RESULTS_FILE

# Phase 2: Authentication
log "Phase 2: Authentication Tests"

# Register new user
RANDOM_EMAIL="test-$TIMESTAMP@example.com"
test_api "User Registration" "POST" "/auth/register" \
    "{\"email\":\"$RANDOM_EMAIL\",\"password\":\"Test123!\",\"full_name\":\"Test User\"}" \
    "201"

# Login with admin
ADMIN_LOGIN=$(curl -s -X POST $API_URL/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@agridao.com","password":"admin123"}')

ADMIN_TOKEN=$(echo $ADMIN_LOGIN | jq -r '.access_token // empty')

if [ -z "$ADMIN_TOKEN" ]; then
    error "Failed to get admin token"
    ADMIN_TOKEN="invalid"
else
    log "Admin login successful"
fi

test_api "Admin Login" "POST" "/auth/login" \
    "{\"email\":\"admin@agridao.com\",\"password\":\"admin123\"}" \
    "200"

test_api "Get Current User" "GET" "/auth/me" "" "200" "$ADMIN_TOKEN"
echo "" | tee -a $RESULTS_FILE

# Phase 3: Marketplace
log "Phase 3: Marketplace Tests"
test_api "List Products" "GET" "/marketplace/products" "" "200"
test_api "Search Products" "GET" "/marketplace/products?search=rice" "" "200"
test_api "Get Product Categories" "GET" "/marketplace/categories" "" "200"
echo "" | tee -a $RESULTS_FILE

# Phase 4: Cart Operations
log "Phase 4: Cart Tests"
test_api "Get Cart" "GET" "/cart" "" "200" "$ADMIN_TOKEN"
test_api "Add to Cart" "POST" "/cart/items" \
    "{\"product_id\":1,\"quantity\":2}" \
    "201" "$ADMIN_TOKEN"
test_api "Update Cart Item" "PUT" "/cart/items/1" \
    "{\"quantity\":3}" \
    "200" "$ADMIN_TOKEN"
echo "" | tee -a $RESULTS_FILE

# Phase 5: Orders
log "Phase 5: Order Tests"
test_api "List Orders" "GET" "/orders" "" "200" "$ADMIN_TOKEN"
test_api "Get Order Details" "GET" "/orders/1" "" "200" "$ADMIN_TOKEN"
echo "" | tee -a $RESULTS_FILE

# Phase 6: Funding
log "Phase 6: Funding Tests"
test_api "List Funding Requests" "GET" "/finance/funding-requests" "" "200"
test_api "Get Funding Stats" "GET" "/finance/stats" "" "200"
echo "" | tee -a $RESULTS_FILE

# Phase 7: Admin Operations
log "Phase 7: Admin Tests"
test_api "List Users (Admin)" "GET" "/admin/users" "" "200" "$ADMIN_TOKEN"
test_api "Get Analytics" "GET" "/analytics/dashboard" "" "200" "$ADMIN_TOKEN"
test_api "System Stats" "GET" "/admin/stats" "" "200" "$ADMIN_TOKEN"
echo "" | tee -a $RESULTS_FILE

# Phase 8: Social Features
log "Phase 8: Social Features Tests"
test_api "List Posts" "GET" "/social/posts" "" "200"
test_api "Get Notifications" "GET" "/notifications" "" "200" "$ADMIN_TOKEN"
echo "" | tee -a $RESULTS_FILE

# Phase 9: AI & Recommendations
log "Phase 9: AI & Recommendations Tests"
test_api "Get Recommendations" "GET" "/recommendations" "" "200" "$ADMIN_TOKEN"
test_api "Weather Data" "GET" "/ai/weather?location=Dhaka" "" "200"
echo "" | tee -a $RESULTS_FILE

# Phase 10: Performance Tests
log "Phase 10: Performance Tests"

# Test response times
log "Testing API response times..."
for i in {1..10}; do
    start=$(date +%s%N)
    curl -s $API_URL/health > /dev/null
    end=$(date +%s%N)
    duration=$(( (end - start) / 1000000 ))
    echo "  Request $i: ${duration}ms" >> $RESULTS_FILE
done
echo "" | tee -a $RESULTS_FILE

# Generate Summary
log "=== Test Summary ==="
log "Total Tests: $TOTAL_TESTS"
log "Passed: $PASSED_TESTS"
log "Failed: $FAILED_TESTS"
log "Success Rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
echo "" | tee -a $RESULTS_FILE

# Generate JSON report
cat > $JSON_FILE <<EOF
{
  "timestamp": "$TIMESTAMP",
  "api_url": "$API_URL",
  "total_tests": $TOTAL_TESTS,
  "passed": $PASSED_TESTS,
  "failed": $FAILED_TESTS,
  "success_rate": $(( PASSED_TESTS * 100 / TOTAL_TESTS )),
  "results_file": "$RESULTS_FILE"
}
EOF

log "Results saved to:"
log "  - Text: $RESULTS_FILE"
log "  - JSON: $JSON_FILE"

# Exit with appropriate code
if [ $FAILED_TESTS -eq 0 ]; then
    log "All tests passed! ✓"
    exit 0
else
    error "$FAILED_TESTS test(s) failed"
    exit 1
fi
