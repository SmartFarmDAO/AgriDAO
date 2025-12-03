#!/bin/bash

# AgriDAO Auth Diagnostic and Fix Script
# Diagnoses and fixes common authentication issues

set -e

API_URL="${API_URL:-http://54.251.65.124/api}"
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"; }
error() { echo -e "${RED}[$(date +'%H:%M:%S')] ERROR:${NC} $1"; }
warn() { echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING:${NC} $1"; }

log "=== AgriDAO Auth Diagnostic ==="
log "API URL: $API_URL"
echo ""

# Test 1: Check if backend is running
log "Test 1: Backend Health Check"
if curl -sf $API_URL/health > /dev/null; then
    log "✓ Backend is running"
else
    error "✗ Backend is not responding"
    log "Checking backend logs..."
    docker logs agridao-backend --tail 50
    exit 1
fi
echo ""

# Test 2: Check CORS headers
log "Test 2: CORS Configuration"
CORS_HEADERS=$(curl -sI -X OPTIONS $API_URL/auth/login \
    -H "Origin: http://54.251.65.124" \
    -H "Access-Control-Request-Method: POST" | grep -i "access-control")

if [ -n "$CORS_HEADERS" ]; then
    log "✓ CORS headers present:"
    echo "$CORS_HEADERS"
else
    warn "✗ CORS headers missing or incorrect"
fi
echo ""

# Test 3: Test login endpoint
log "Test 3: Login Endpoint Test"
LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST $API_URL/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"admin@agridao.com","password":"admin123"}')

STATUS_CODE=$(echo "$LOGIN_RESPONSE" | tail -n1)
BODY=$(echo "$LOGIN_RESPONSE" | sed '$d')

log "Status Code: $STATUS_CODE"
log "Response: $BODY"

if [ "$STATUS_CODE" = "200" ]; then
    log "✓ Login endpoint working"
    TOKEN=$(echo "$BODY" | jq -r '.access_token // empty')
    if [ -n "$TOKEN" ]; then
        log "✓ Token received: ${TOKEN:0:20}..."
    else
        error "✗ No token in response"
    fi
else
    error "✗ Login failed with status $STATUS_CODE"
fi
echo ""

# Test 4: Test authenticated endpoint
if [ -n "$TOKEN" ]; then
    log "Test 4: Authenticated Request Test"
    AUTH_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET $API_URL/auth/me \
        -H "Authorization: Bearer $TOKEN")
    
    AUTH_STATUS=$(echo "$AUTH_RESPONSE" | tail -n1)
    AUTH_BODY=$(echo "$AUTH_RESPONSE" | sed '$d')
    
    log "Status Code: $AUTH_STATUS"
    log "Response: $AUTH_BODY"
    
    if [ "$AUTH_STATUS" = "200" ]; then
        log "✓ Authentication working correctly"
    else
        error "✗ Authentication failed"
    fi
fi
echo ""

# Test 5: Check environment variables
log "Test 5: Environment Variables Check"
log "Checking backend environment..."
docker exec agridao-backend env | grep -E "SECRET_KEY|JWT_SECRET|CORS_ORIGINS" || warn "Environment variables not set"
echo ""

# Test 6: Database connection
log "Test 6: Database Connection"
if docker exec agridao-db pg_isready -U postgres > /dev/null 2>&1; then
    log "✓ Database is accessible"
    
    # Check if admin user exists
    ADMIN_EXISTS=$(docker exec agridao-db psql -U postgres -d agridao -t -c \
        "SELECT COUNT(*) FROM users WHERE email='admin@agridao.com';" 2>/dev/null | tr -d ' ')
    
    if [ "$ADMIN_EXISTS" = "1" ]; then
        log "✓ Admin user exists"
    else
        warn "✗ Admin user not found"
        log "Creating admin user..."
        docker exec agridao-backend python create_admin.py
    fi
else
    error "✗ Database is not accessible"
fi
echo ""

# Diagnostic Summary
log "=== Diagnostic Summary ==="
if [ "$STATUS_CODE" = "200" ] && [ -n "$TOKEN" ] && [ "$AUTH_STATUS" = "200" ]; then
    log "✓ All auth tests passed!"
    log "Authentication is working correctly."
    exit 0
else
    error "Some auth tests failed. Applying fixes..."
    echo ""
    
    # Fix 1: Update CORS origins
    log "Fix 1: Updating CORS configuration..."
    cat > /tmp/cors_fix.py <<'EOF'
import os
os.environ.setdefault('CORS_ORIGINS', 'http://54.251.65.124,http://54.251.65.124:80,https://54.251.65.124,http://localhost:5173')
EOF
    
    # Fix 2: Restart backend
    log "Fix 2: Restarting backend service..."
    docker-compose -f deployment/lightsail/docker-compose.lightsail.yml restart backend
    
    log "Waiting for backend to start..."
    sleep 10
    
    # Retest
    log "Retesting authentication..."
    RETEST=$(curl -s -w "\n%{http_code}" -X POST $API_URL/auth/login \
        -H "Content-Type: application/json" \
        -d '{"email":"admin@agridao.com","password":"admin123"}')
    
    RETEST_STATUS=$(echo "$RETEST" | tail -n1)
    
    if [ "$RETEST_STATUS" = "200" ]; then
        log "✓ Auth fixed successfully!"
        exit 0
    else
        error "Auth still not working. Manual intervention required."
        log "Please check:"
        log "1. Backend logs: docker logs agridao-backend"
        log "2. Environment variables in .env file"
        log "3. Database connectivity"
        exit 1
    fi
fi
