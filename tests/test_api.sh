#!/bin/bash

# Quick API Test Sequence for Universal Service
# Prerequisites: kubectl port-forward must be running
# Usage: ./tests/test_api.sh

set -e

BASE_URL="http://localhost:8000"

echo "🧪 Testing Universal Service API"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print test step
print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

# Function to print response
print_response() {
    echo -e "${GREEN}✓ Response:${NC}"
    echo "$1" | python3 -m json.tool 2>/dev/null || echo "$1"
    echo ""
}

# Check if service is accessible
print_step "1. Health Check"
response=$(curl -s "$BASE_URL/health")
print_response "$response"

# Check root endpoint
print_step "2. Root Endpoint Check"
response=$(curl -s "$BASE_URL/")
print_response "$response"

# Create an item
print_step "3. Create Item (MacBook Pro)"
response=$(curl -s -X POST "$BASE_URL/api/items" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MacBook Pro",
    "description": "16 inch M3 Pro",
    "price": 2499.99
  }')
print_response "$response"

# Extract item ID from response (assuming JSON response)
ITEM_ID=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null || echo "1")

# List all items
print_step "4. List All Items"
response=$(curl -s "$BASE_URL/api/items")
print_response "$response"

# Get item by ID
print_step "5. Get Item by ID ($ITEM_ID)"
response=$(curl -s "$BASE_URL/api/items/$ITEM_ID")
print_response "$response"

# Update the item
print_step "6. Update Item ($ITEM_ID) - Change price"
response=$(curl -s -X PUT "$BASE_URL/api/items/$ITEM_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "price": 2299.99
  }')
print_response "$response"

# Verify update
print_step "7. Verify Update - Get Item ($ITEM_ID) again"
response=$(curl -s "$BASE_URL/api/items/$ITEM_ID")
print_response "$response"

# Create another item
print_step "8. Create Another Item (iPhone 15)"
response=$(curl -s -X POST "$BASE_URL/api/items" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "iPhone 15",
    "description": "128GB Pro",
    "price": 999.99
  }')
print_response "$response"

# List all items again
print_step "9. List All Items (should have 2 items now)"
response=$(curl -s "$BASE_URL/api/items")
print_response "$response"

# Delete first item
print_step "10. Delete Item ($ITEM_ID)"
response=$(curl -s -w "\nHTTP Status: %{http_code}\n" -X DELETE "$BASE_URL/api/items/$ITEM_ID")
echo "$response"
echo ""

# List all items after deletion
print_step "11. List All Items (should have 1 item now)"
response=$(curl -s "$BASE_URL/api/items")
print_response "$response"

echo -e "${GREEN}✅ All tests completed!${NC}"
echo ""
echo "📚 Interactive API docs available at: $BASE_URL/docs"

