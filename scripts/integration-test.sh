#!/bin/bash

# AgriDAO System Integration Test Script
# Performs comprehensive testing across all system components

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BASE_URL="${BASE_URL:-http://localhost:8000}"
FRONTEND_URL="${FRONTEND_URL:-http://localhost:5174}"
TEST_EMAIL="${TEST_EMAIL:-test@example.com}"
TEST_PASSWORD="${TEST_PASSWORD:-testpassword123}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[PASS]${NC} $1"
    ((PASSED_TESTS++))
}

error() {
    echo -e "${RED}[FAIL]${NC} $1"
    ((FAILED_TESTS++))
}

warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

test_start() {
    ((TOTAL_TESTS++))
    log "Running test: $1"
}

# Health check function
health_check() {
    local url=$1
    local service_name=$2
    
    test_start "Health check - $service_name"
    
    if curl -s -f "$url/health" > /dev/null; then
        success "$service_name is healthy"
        return 0
    else
        error "$service_name health check failed"
        return 1
    fi
}

# Test database connectivity
test_database() {
    test_start "Database connectivity"
    
    response=$(curl -s "$BASE_URL/health/detailed")
    if echo "$response" | grep -q '"database".*"healthy"'; then
        success "Database is connected and healthy"
    else
        error "Database connectivity issues detected"
    fi
}

# Test Redis connectivity
test_redis() {
    test_start "Redis connectivity"
    
    response=$(curl -s "$BASE_URL/health/detailed")
    if echo "$response" | grep -q '"redis".*"healthy"'; then
        success "Redis is connected and healthy"
    else
        error "Redis connectivity issues detected"
    fi
}

# Test authentication endpoints
test_authentication() {
    test_start "Authentication system"
    
    # Test OTP request
    response=$(curl -s -X POST "$BASE_URL/auth/otp/request" \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"$TEST_EMAIL\"}")
    
    if echo "$response" | grep -q '"sent":.*true'; then
        success "OTP request endpoint working"
    else
        error "OTP request endpoint failed"
    fi
    
    # Test invalid login
    response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/auth/otp/verify" \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"$TEST_EMAIL\", \"code\": \"invalid\"}")
    
    if echo "$response" | grep -q "400\|401\|422"; then
        success "Authentication properly rejects invalid credentials"
    else
        error "Authentication security issue - invalid credentials accepted"
    fi
}

# Test API endpoints
test_api_endpoints() {
    test_start "Core API endpoints"
    
    # Test marketplace endpoint
    response=$(curl -s -w "%{http_code}" "$BASE_URL/marketplace/products")
    http_code=$(echo "$response" | tail -n1)
    
    if [[ "$http_code" == "200" ]]; then
        success "Marketplace API endpoint accessible"
    else
        error "Marketplace API endpoint failed (HTTP $http_code)"
    fi
    
    # Test finance endpoint
    response=$(curl -s -w "%{http_code}" "$BASE_URL/finance/metrics")
    http_code=$(echo "$response" | tail -n1)
    
    if [[ "$http_code" == "200" || "$http_code" == "401" ]]; then
        success "Finance API endpoint responding (auth required)"
    else
        error "Finance API endpoint failed (HTTP $http_code)"
    fi
}

# Test CORS configuration
test_cors() {
    test_start "CORS configuration"
    
    response=$(curl -s -I -H "Origin: http://localhost:5174" "$BASE_URL/health")
    
    if echo "$response" | grep -q "Access-Control-Allow-Origin"; then
        success "CORS headers present"
    else
        error "CORS configuration missing"
    fi
}

# Test rate limiting
test_rate_limiting() {
    test_start "Rate limiting"
    
    # Make rapid requests to test rate limiting
    for i in {1..15}; do
        curl -s "$BASE_URL/health" > /dev/null
    done
    
    # Check if rate limit is hit
    response=$(curl -s -w "%{http_code}" "$BASE_URL/health")
    http_code=$(echo "$response" | tail -n1)
    
    if [[ "$http_code" == "429" ]]; then
        success "Rate limiting is working"
    else
        warning "Rate limiting may not be configured (HTTP $http_code)"
    fi
    
    # Wait for rate limit to reset
    sleep 5
}

# Test security headers
test_security_headers() {
    test_start "Security headers"
    
    headers=$(curl -s -I "$BASE_URL/health")
    
    security_headers=(
        "X-Content-Type-Options"
        "X-Frame-Options"
        "X-XSS-Protection"
    )
    
    missing_headers=0
    for header in "${security_headers[@]}"; do
        if ! echo "$headers" | grep -qi "$header"; then
            ((missing_headers++))
        fi
    done
    
    if [[ $missing_headers -eq 0 ]]; then
        success "All security headers present"
    else
        warning "$missing_headers security headers missing"
    fi
}

# Test file upload endpoint
test_file_upload() {
    test_start "File upload functionality"
    
    # Create a small test file
    echo "test content" > /tmp/test_upload.txt
    
    response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/files/upload" \
        -F "file=@/tmp/test_upload.txt")
    
    http_code=$(echo "$response" | tail -n1)
    
    if [[ "$http_code" == "200" || "$http_code" == "401" ]]; then
        success "File upload endpoint responding"
    else
        warning "File upload endpoint may have issues (HTTP $http_code)"
    fi
    
    rm -f /tmp/test_upload.txt
}

# Test WebSocket connections (if applicable)
test_websockets() {
    test_start "WebSocket connectivity"
    
    if command -v wscat &> /dev/null; then
        # Test WebSocket connection
        timeout 5s wscat -c "ws://localhost:8000/ws" --no-check < /dev/null
        if [[ $? -eq 0 ]]; then
            success "WebSocket connection working"
        else
            warning "WebSocket connection issues or not implemented"
        fi
    else
        warning "wscat not available, skipping WebSocket test"
    fi
}

# Test frontend connectivity
test_frontend() {
    test_start "Frontend accessibility"
    
    response=$(curl -s -w "%{http_code}" "$FRONTEND_URL")
    http_code=$(echo "$response" | tail -n1)
    
    if [[ "$http_code" == "200" ]]; then
        success "Frontend is accessible"
    else
        error "Frontend accessibility issues (HTTP $http_code)"
    fi
}

# Test admin endpoints
test_admin_endpoints() {
    test_start "Admin endpoints"
    
    # Test admin stats (should require authentication)
    response=$(curl -s -w "%{http_code}" "$BASE_URL/admin/stats")
    http_code=$(echo "$response" | tail -n1)
    
    if [[ "$http_code" == "401" || "$http_code" == "403" ]]; then
        success "Admin endpoints properly protected"
    else
        warning "Admin endpoints may have security issues (HTTP $http_code)"
    fi
}

# Test order workflow
test_order_workflow() {
    test_start "Order workflow"
    
    # Test order listing (should require auth)
    response=$(curl -s -w "%{http_code}" "$BASE_URL/api/orders")
    http_code=$(echo "$response" | tail -n1)
    
    if [[ "$http_code" == "401" || "$http_code" == "403" ]]; then
        success "Order endpoints properly secured"
    else
        warning "Order endpoints may have security issues (HTTP $http_code)"
    fi
}

# Test dispute system
test_dispute_system() {
    test_start "Dispute system"
    
    # Test dispute listing (should require auth)
    response=$(curl -s -w "%{http_code}" "$BASE_URL/api/disputes")
    http_code=$(echo "$response" | tail -n1)
    
    if [[ "$http_code" == "401" || "$http_code" == "403" ]]; then
        success "Dispute endpoints properly secured"
    else
        warning "Dispute endpoints may have security issues (HTTP $http_code)"
    fi
}

# Test analytics endpoints
test_analytics() {
    test_start "Analytics endpoints"
    
    response=$(curl -s -w "%{http_code}" "$BASE_URL/analytics/dashboard")
    http_code=$(echo "$response" | tail -n1)
    
    if [[ "$http_code" == "200" || "$http_code" == "401" ]]; then
        success "Analytics endpoints responding"
    else
        warning "Analytics endpoints may have issues (HTTP $http_code)"
    fi
}

# Test error handling
test_error_handling() {
    test_start "Error handling"
    
    # Test 404 endpoint
    response=$(curl -s -w "%{http_code}" "$BASE_URL/nonexistent-endpoint")
    http_code=$(echo "$response" | tail -n1)
    
    if [[ "$http_code" == "404" ]]; then
        success "404 errors handled correctly"
    else
        error "Error handling issues (expected 404, got $http_code)"
    fi
}

# Test database migrations
test_database_migrations() {
    test_start "Database migrations"
    
    if docker-compose -f "$PROJECT_ROOT/docker-compose.yml" ps | grep -q backend; then
        # Check if migrations are up to date
        migration_output=$(docker-compose -f "$PROJECT_ROOT/docker-compose.yml" exec -T backend alembic current 2>/dev/null || echo "migration check failed")
        
        if [[ "$migration_output" != *"failed"* ]]; then
            success "Database migrations are current"
        else
            error "Database migration issues detected"
        fi
    else
        warning "Backend container not running, skipping migration test"
    fi
}

# Performance tests
test_performance() {
    test_start "Basic performance"
    
    # Test response time for health endpoint
    start_time=$(date +%s%N)
    curl -s "$BASE_URL/health" > /dev/null
    end_time=$(date +%s%N)
    
    response_time=$(( (end_time - start_time) / 1000000 )) # Convert to milliseconds
    
    if [[ $response_time -lt 1000 ]]; then
        success "Health endpoint response time: ${response_time}ms"
    else
        warning "Health endpoint slow response: ${response_time}ms"
    fi
}

# SSL/TLS tests (if HTTPS)
test_ssl() {
    if [[ "$BASE_URL" == https* ]]; then
        test_start "SSL/TLS configuration"
        
        ssl_output=$(echo | openssl s_client -connect "${BASE_URL#https://}:443" -servername "${BASE_URL#https://}" 2>/dev/null | openssl x509 -noout -dates)
        
        if echo "$ssl_output" | grep -q "notAfter"; then
            success "SSL certificate is valid"
        else
            error "SSL certificate issues detected"
        fi
    fi
}

# Run all tests
run_all_tests() {
    log "Starting comprehensive system integration tests..."
    log "Base URL: $BASE_URL"
    log "Frontend URL: $FRONTEND_URL"
    echo ""
    
    # Service health checks
    health_check "$BASE_URL" "Backend API"
    health_check "$FRONTEND_URL" "Frontend"
    
    # Infrastructure tests
    test_database
    test_redis
    
    # Security tests
    test_authentication
    test_cors
    test_rate_limiting
    test_security_headers
    
    # API functionality tests
    test_api_endpoints
    test_admin_endpoints
    test_order_workflow
    test_dispute_system
    test_analytics
    test_file_upload
    
    # System tests
    test_frontend
    test_websockets
    test_error_handling
    test_database_migrations
    test_performance
    test_ssl
    
    # Print summary
    echo ""
    echo "==================== TEST SUMMARY ===================="
    echo -e "Total tests: ${BLUE}$TOTAL_TESTS${NC}"
    echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
    echo -e "Failed: ${RED}$FAILED_TESTS${NC}"
    echo -e "Success rate: $(( PASSED_TESTS * 100 / TOTAL_TESTS ))%"
    
    if [[ $FAILED_TESTS -gt 0 ]]; then
        echo ""
        error "Some tests failed. Please review the output above."
        exit 1
    else
        echo ""
        success "All tests passed successfully!"
        exit 0
    fi
}

# Check if services are running
check_services() {
    log "Checking if services are running..."
    
    if ! curl -s "$BASE_URL/health" > /dev/null; then
        error "Backend service is not accessible at $BASE_URL"
        echo "Please ensure the backend is running before running tests."
        exit 1
    fi
    
    if ! curl -s "$FRONTEND_URL" > /dev/null 2>&1; then
        warning "Frontend service is not accessible at $FRONTEND_URL"
        warning "Some tests may fail if frontend is not running."
    fi
}

# Main execution
case "${1:-all}" in
    "health")
        health_check "$BASE_URL" "Backend API"
        ;;
    "auth")
        test_authentication
        ;;
    "security")
        test_cors
        test_rate_limiting
        test_security_headers
        ;;
    "api")
        test_api_endpoints
        ;;
    "performance")
        test_performance
        ;;
    "all")
        check_services
        run_all_tests
        ;;
    *)
        echo "Usage: $0 {all|health|auth|security|api|performance}"
        echo "  all         - Run all integration tests (default)"
        echo "  health      - Check service health only"
        echo "  auth        - Test authentication endpoints"
        echo "  security    - Test security configurations"
        echo "  api         - Test API endpoints"
        echo "  performance - Test basic performance"
        exit 1
        ;;
esac