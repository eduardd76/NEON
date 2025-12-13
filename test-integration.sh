#!/bin/bash
# NEON Integration Test Script
# Run this script to verify all components are working

set -e  # Exit on error

echo "============================================"
echo "NEON Integration Test Suite"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo -n "Testing: $test_name... "

    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Function to run test with output check
run_test_with_check() {
    local test_name="$1"
    local test_command="$2"
    local expected="$3"

    echo -n "Testing: $test_name... "

    result=$(eval "$test_command" 2>/dev/null)

    if echo "$result" | grep -q "$expected"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAILED${NC}"
        echo "  Expected to find: $expected"
        echo "  Got: $result"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo "1. Checking Prerequisites"
echo "-------------------------"

run_test "Docker is running" "docker ps"
run_test "Python is installed" "python --version"
run_test "Node.js is installed" "node --version"

echo ""
echo "2. Checking Services"
echo "-------------------"

run_test "Database container running" "docker ps | grep neon_db"
run_test "Backend container running" "docker ps | grep neon_backend"

echo ""
echo "3. Testing Backend API"
echo "---------------------"

run_test_with_check "Health endpoint" "curl -s http://localhost:8000/health" "healthy"
run_test_with_check "Vendors endpoint" "curl -s http://localhost:8000/api/v1/images/vendors/" "cisco"
run_test_with_check "Images endpoint" "curl -s http://localhost:8000/api/v1/images/" "ceos"
run_test_with_check "Chat suggestions" "curl -s http://localhost:8000/api/v1/chat/suggestions" "suggestions"

echo ""
echo "4. Testing Lab Operations"
echo "------------------------"

# Create a test lab
echo -n "Creating test lab... "
LAB_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/labs/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Integration Test Lab", "description": "Automated test"}')

if echo "$LAB_RESPONSE" | grep -q "Integration Test Lab"; then
    echo -e "${GREEN}✓ PASSED${NC}"
    ((TESTS_PASSED++))

    # Extract lab ID
    LAB_ID=$(echo "$LAB_RESPONSE" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    echo "  Lab ID: $LAB_ID"

    # Get first image ID
    IMAGE_ID=$(curl -s http://localhost:8000/api/v1/images/ | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)

    # Add a node
    echo -n "Adding node to lab... "
    NODE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/labs/$LAB_ID/nodes \
      -H "Content-Type: application/json" \
      -d "{\"name\": \"TestRouter\", \"image_id\": \"$IMAGE_ID\", \"position_x\": 100, \"position_y\": 100}")

    if echo "$NODE_RESPONSE" | grep -q "TestRouter"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((TESTS_FAILED++))
    fi

    # Get lab details
    echo -n "Retrieving lab details... "
    LAB_DETAILS=$(curl -s http://localhost:8000/api/v1/labs/$LAB_ID)

    if echo "$LAB_DETAILS" | grep -q "TestRouter"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((TESTS_FAILED++))
    fi

    # Clean up - delete lab
    echo -n "Deleting test lab... "
    DELETE_RESPONSE=$(curl -s -X DELETE http://localhost:8000/api/v1/labs/$LAB_ID)

    if echo "$DELETE_RESPONSE" | grep -q "deleted successfully"; then
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${RED}✗ FAILED${NC}"
    ((TESTS_FAILED++))
fi

echo ""
echo "5. Testing Frontend"
echo "------------------"

if [ -d "frontend/dist" ]; then
    echo -e "Frontend build exists: ${GREEN}✓ PASSED${NC}"
    ((TESTS_PASSED++))
else
    echo -e "Frontend build missing: ${YELLOW}⚠ SKIPPED${NC}"
    echo "  Run 'cd frontend && npm run build' to create build"
fi

echo ""
echo "============================================"
echo "Test Results"
echo "============================================"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Open http://localhost:8000/docs in your browser"
    echo "  2. Start frontend: cd frontend && npm run dev"
    echo "  3. Open http://localhost:5173 to see the UI"
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check docker-compose logs: docker-compose logs"
    echo "  2. Verify services: docker-compose ps"
    echo "  3. Restart services: docker-compose restart"
    exit 1
fi
