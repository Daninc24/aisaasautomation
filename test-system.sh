#!/bin/bash

# AutomateIQ System Test Script
# This script tests all components of the AutomateIQ system

echo "🧪 AutomateIQ System Test Suite"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    print_test "$test_name"
    
    if eval "$test_command" > /dev/null 2>&1; then
        print_pass "$test_name"
        ((TESTS_PASSED++))
        return 0
    else
        print_fail "$test_name"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo ""
echo "📋 Testing Prerequisites..."

# Test Node.js
run_test "Node.js installation" "node --version"

# Test Python
run_test "Python installation" "python3 --version"

# Test npm
run_test "npm installation" "npm --version"

# Test Docker (optional)
if command -v docker &> /dev/null; then
    run_test "Docker installation" "docker --version"
else
    print_warn "Docker not found (optional)"
fi

echo ""
echo "📦 Testing Dependencies..."

# Test frontend dependencies
run_test "Frontend dependencies" "npm list --depth=0"

# Test backend dependencies
run_test "Backend dependencies" "cd backend && npm list --depth=0"

# Test AI engine dependencies
run_test "AI engine Python virtual environment" "test -d ai-engine/venv"

echo ""
echo "🔧 Testing Configuration..."

# Test environment file
run_test "Environment file exists" "test -f .env"

# Test uploads directory
run_test "Uploads directory" "test -d uploads || mkdir -p uploads"

echo ""
echo "🤖 Testing AI Engine..."

# Test AI engine imports
run_test "AI engine imports" "cd ai-engine && source venv/bin/activate && CUDA_VISIBLE_DEVICES='' python -c 'from app.main import app'"

# Test spaCy model
run_test "spaCy model" "cd ai-engine && source venv/bin/activate && python -c 'import spacy; spacy.load(\"en_core_web_sm\")'"

# Test OCR dependencies
run_test "Tesseract OCR" "which tesseract"

echo ""
echo "🌐 Testing API Endpoints (if services are running)..."

# Function to test endpoint
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_status="$3"
    
    print_test "$name"
    
    if command -v curl &> /dev/null; then
        local status=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
        if [ "$status" = "$expected_status" ]; then
            print_pass "$name (Status: $status)"
            ((TESTS_PASSED++))
        else
            print_warn "$name (Status: $status, Expected: $expected_status) - Service may not be running"
        fi
    else
        print_warn "$name - curl not available"
    fi
}

# Test endpoints (only if services are running)
test_endpoint "Backend health check" "http://localhost:5000/health" "200"
test_endpoint "AI engine health check" "http://localhost:8000/health" "200"
test_endpoint "Frontend (if running)" "http://localhost:5173" "200"

echo ""
echo "📁 Testing File Structure..."

# Test critical files
critical_files=(
    "package.json"
    "backend/package.json"
    "ai-engine/requirements.txt"
    "docker-compose.yml"
    ".gitignore"
    ".env.example"
    "README.md"
    "ARCHITECTURE.md"
    "DEPLOYMENT.md"
    "SECURITY.md"
)

for file in "${critical_files[@]}"; do
    run_test "File exists: $file" "test -f $file"
done

echo ""
echo "🔒 Testing Security Configuration..."

# Test .env is gitignored
run_test ".env file is gitignored" "grep -q '\.env' .gitignore"

# Test secrets are not in git
run_test "No secrets in git history" "! git log --all --full-history -- .env 2>/dev/null | grep -q '.'"

echo ""
echo "📊 Test Results Summary"
echo "======================"
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo -e "Total Tests: $((TESTS_PASSED + TESTS_FAILED))"

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "\n${GREEN}🎉 All tests passed! Your AutomateIQ system is ready.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Configure your .env file with actual API keys"
    echo "2. Start the services:"
    echo "   - Docker: docker-compose up -d"
    echo "   - Manual: npm run dev (in separate terminals)"
    echo "3. Access the application at http://localhost:5173"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please check the issues above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "- Run ./setup.sh to install missing dependencies"
    echo "- Check .env file configuration"
    echo "- Ensure all services are properly installed"
    exit 1
fi