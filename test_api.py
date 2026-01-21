"""
Quick Test Script
=================

Test the OAuth2 API to make sure everything works!
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("\n" + "="*60)
print("Testing OAuth2 API")
print("="*60 + "\n")

# Test 1: Root endpoint
print("1. Testing root endpoint...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"   ✅ Status: {response.status_code}")
    print(f"   Response: {response.json()['message']}\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")

# Test 2: Login with valid credentials
print("2. Testing login with valid credentials...")
try:
    response = requests.post(
        f"{BASE_URL}/token",
        data={"username": "john", "password": "secret"}
    )
    print(f"   ✅ Status: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        print(f"   ✅ Token received: {token[:50]}...\n")
        
        # Test 3: Access protected endpoint
        print("3. Testing protected endpoint with token...")
        response = requests.get(
            f"{BASE_URL}/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"   ✅ Status: {response.status_code}")
        user_data = response.json()
        print(f"   ✅ User: {user_data['username']} ({user_data['full_name']})\n")
        
        # Test 4: Get user items
        print("4. Testing user items endpoint...")
        response = requests.get(
            f"{BASE_URL}/users/me/items",
            headers={"Authorization": f"Bearer {token}"}
        )
        print(f"   ✅ Status: {response.status_code}")
        items_data = response.json()
        print(f"   ✅ Items: {len(items_data['items'])} items found\n")
    else:
        print(f"   ❌ Login failed: {response.json()}\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")

# Test 5: Login with wrong credentials
print("5. Testing login with wrong credentials...")
try:
    response = requests.post(
        f"{BASE_URL}/token",
        data={"username": "john", "password": "wrongpassword"}
    )
    print(f"   ✅ Status: {response.status_code} (should be 401)")
    print(f"   ✅ Error message: {response.json()['detail']}\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")

# Test 6: Access protected endpoint without token
print("6. Testing protected endpoint without token...")
try:
    response = requests.get(f"{BASE_URL}/users/me")
    print(f"   ✅ Status: {response.status_code} (should be 401)")
    print(f"   ✅ Error message: {response.json()['detail']}\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")

print("="*60)
print("✅ All tests completed!")
print("="*60 + "\n")

print("💡 Next steps:")
print("   - Visit http://127.0.0.1:8000/docs for interactive API docs")
print("   - Try the tutorial files in the tutorial/ directory")
print("   - Check API_EXAMPLES.md for more examples\n")
