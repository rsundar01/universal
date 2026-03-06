#!/usr/bin/env python3
"""
Python test script for Universal Service API
Usage: python tests/test_api.py
"""

import requests
import json
import sys
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def print_step(step: str):
    """Print a test step header"""
    print(f"\n▶ {step}")
    print("-" * 50)


def print_response(response: requests.Response, data: Any = None):
    """Print formatted response"""
    print(f"Status: {response.status_code}")
    if data:
        print(f"Response: {json.dumps(data, indent=2)}")
    print()


def test_health_check():
    """Test health check endpoint"""
    print_step("1. Health Check")
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, response.json())


def test_root_endpoint():
    """Test root endpoint"""
    print_step("2. Root Endpoint")
    response = requests.get(f"{BASE_URL}/")
    print_response(response, response.json())


def test_create_item() -> int:
    """Test creating an item"""
    print_step("3. Create Item (MacBook Pro)")
    item_data = {
        "name": "MacBook Pro",
        "description": "16 inch M3 Pro",
        "price": 2499.99
    }
    response = requests.post(f"{BASE_URL}/api/items", json=item_data)
    print_response(response, response.json())
    return response.json()["id"]


def test_get_all_items():
    """Test getting all items"""
    print_step("4. List All Items")
    response = requests.get(f"{BASE_URL}/api/items")
    print_response(response, response.json())


def test_get_item_by_id(item_id: int):
    """Test getting item by ID"""
    print_step(f"5. Get Item by ID ({item_id})")
    response = requests.get(f"{BASE_URL}/api/items/{item_id}")
    print_response(response, response.json())


def test_update_item(item_id: int):
    """Test updating an item"""
    print_step(f"6. Update Item ({item_id}) - Change price")
    update_data = {
        "price": 2299.99
    }
    response = requests.put(f"{BASE_URL}/api/items/{item_id}", json=update_data)
    print_response(response, response.json())


def test_delete_item(item_id: int):
    """Test deleting an item"""
    print_step(f"7. Delete Item ({item_id})")
    response = requests.delete(f"{BASE_URL}/api/items/{item_id}")
    print(f"Status: {response.status_code}")
    if response.status_code == 204:
        print("Item deleted successfully")
    print()


def main():
    """Run all tests"""
    print("🧪 Testing Universal Service API")
    print("=" * 50)
    
    try:
        # Test basic endpoints
        test_health_check()
        test_root_endpoint()
        
        # Test CRUD operations
        item_id = test_create_item()
        test_get_all_items()
        test_get_item_by_id(item_id)
        test_update_item(item_id)
        test_get_item_by_id(item_id)  # Verify update
        
        # Create another item
        print_step("8. Create Another Item (iPhone 15)")
        item_data2 = {
            "name": "iPhone 15",
            "description": "128GB Pro",
            "price": 999.99
        }
        response = requests.post(f"{BASE_URL}/api/items", json=item_data2)
        print_response(response, response.json())
        item_id2 = response.json()["id"]
        
        # List all items
        test_get_all_items()
        
        # Delete first item
        test_delete_item(item_id)
        
        # List all items after deletion
        test_get_all_items()
        
        print("\n✅ All tests completed!")
        print(f"\n📚 Interactive API docs available at: {BASE_URL}/docs")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to the API.")
        print("Make sure kubectl port-forward is running:")
        print("  kubectl port-forward service/universal-service 8000:80")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

