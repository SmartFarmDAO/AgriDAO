#!/bin/bash

echo "🧪 Testing New Features Implementation"
echo "======================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to test file existence
test_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} $2"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $2 - File not found: $1"
        ((FAILED++))
    fi
}

# Function to test content
test_content() {
    if grep -q "$2" "$1" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $3"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $3"
        ((FAILED++))
    fi
}

echo "📦 Backend Tests"
echo "----------------"

# Backend files
test_file "backend/app/routers/social.py" "Social router exists"
test_file "backend/app/routers/supplychain.py" "Supply chain router exists"
test_file "backend/app/routers/blockchain.py" "Blockchain router exists"

# Backend content
test_content "backend/app/routers/social.py" "def create_post" "Social: create_post function"
test_content "backend/app/routers/social.py" "def like_post" "Social: like_post function"
test_content "backend/app/routers/supplychain.py" "def add_tracking_event" "Supply chain: tracking event function"
test_content "backend/app/routers/blockchain.py" "def create_transaction" "Blockchain: create_transaction function"
test_content "backend/app/main.py" "social.router" "Main: social router registered"
test_content "backend/app/main.py" "blockchain.router" "Main: blockchain router registered"

echo ""
echo "🎨 Frontend Tests"
echo "-----------------"

# Frontend files
test_file "frontend/src/components/Community.tsx" "Community component exists"
test_file "frontend/src/components/SupplyChain.tsx" "SupplyChain component exists"
test_file "frontend/src/components/Blockchain.tsx" "Blockchain component exists"
test_file "frontend/src/pages/Community.tsx" "Community page exists"
test_file "frontend/src/pages/BlockchainPage.tsx" "Blockchain page exists"

# Frontend content
test_content "frontend/src/components/Community.tsx" "createPost" "Community: createPost function"
test_content "frontend/src/components/Community.tsx" "likePost" "Community: likePost function"
test_content "frontend/src/components/SupplyChain.tsx" "createAsset" "Supply chain: createAsset function"
test_content "frontend/src/components/Blockchain.tsx" "createTransaction" "Blockchain: createTransaction function"
test_content "frontend/src/App.tsx" "Community" "App: Community import"
test_content "frontend/src/App.tsx" "BlockchainPage" "App: BlockchainPage import"
test_content "frontend/src/App.tsx" "community" "App: community route"
test_content "frontend/src/App.tsx" "blockchain" "App: blockchain route"

echo ""
echo "📚 Documentation Tests"
echo "----------------------"

# Documentation files
test_file "docs/project/userstory.md" "User stories document exists"
test_file "docs/reports/SOCIAL_FEATURES_IMPLEMENTATION.md" "Social features report exists"
test_file "docs/reports/SUPPLY_CHAIN_IMPLEMENTATION.md" "Supply chain report exists"
test_file "docs/reports/BLOCKCHAIN_IMPLEMENTATION.md" "Blockchain report exists"
test_file "docs/reports/PLATFORM_100_PERCENT_COMPLETE.md" "100% completion report exists"
test_file "docs/guides/NEW_FEATURES_QUICK_REFERENCE.md" "Quick reference guide exists"
test_file "IMPLEMENTATION_COMPLETE.md" "Implementation complete doc exists"

# Documentation content
test_content "docs/project/userstory.md" "100%" "User stories: 100% completion"
test_content "docs/project/userstory.md" "US-11.5: Social Features ✅" "User stories: Social features marked complete"
test_content "docs/project/userstory.md" "US-11.2: Supply Chain Tracking ✅" "User stories: Supply chain marked complete"
test_content "docs/project/userstory.md" "US-11.3: Blockchain Integration ✅" "User stories: Blockchain marked complete"

echo ""
echo "======================================"
echo "📊 Test Results"
echo "======================================"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo "Total: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    exit 1
fi
