# 🔧 API Examples

This guide shows you how to interact with the OAuth2 API using different methods.

## 📋 Table of Contents

1. [Using Swagger UI (Easiest)](#using-swagger-ui)
2. [Using curl (Command Line)](#using-curl)
3. [Using Python Requests](#using-python-requests)
4. [Using JavaScript Fetch](#using-javascript-fetch)
5. [Using Postman](#using-postman)

---

## 🌐 Using Swagger UI

The easiest way to test the API!

### Step 1: Start the server
```bash
uvicorn app:app --reload
```

### Step 2: Open Swagger UI
Navigate to: http://127.0.0.1:8000/docs

### Step 3: Get a token
1. Find the `/token` endpoint
2. Click "Try it out"
3. Enter credentials:
   - **username**: `john`
   - **password**: `secret`
4. Click "Execute"
5. Copy the `access_token` value from the response

### Step 4: Authorize
1. Click the **"Authorize"** button at the top right (🔓 icon)
2. Paste your token in the "Value" field
3. Click "Authorize"
4. Click "Close"

### Step 5: Test protected endpoints
Now try the `/users/me` endpoint - it will automatically include your token!

---

## 💻 Using curl

### 1. Get the Root Information (Public)

```bash
curl -X GET "http://127.0.0.1:8000/"
```

**Response:**
```json
{
  "message": "Welcome to the OAuth2 Tutorial API!",
  "documentation": "/docs",
  "instructions": {
    "step_1": "Get a token from POST /token with username and password",
    "step_2": "Use the token in the Authorization header as 'Bearer <token>'",
    "step_3": "Access protected routes like GET /users/me"
  },
  "test_users": [
    {"username": "john", "password": "secret"},
    {"username": "jane", "password": "secret"}
  ]
}
```

---

### 2. Login and Get Token

```bash
curl -X POST "http://127.0.0.1:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&password=secret"
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2huIiwiZXhwIjoxNzA2MjA1NjAwfQ.abc123...",
  "token_type": "bearer"
}
```

**Save the token:**
```bash
# Extract and save token to a variable
TOKEN=$(curl -X POST "http://127.0.0.1:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&password=secret" \
  | jq -r '.access_token')

echo $TOKEN
```

---

### 3. Access Protected Endpoint (Get Current User)

```bash
curl -X GET "http://127.0.0.1:8000/users/me" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "username": "john",
  "full_name": "John Doe",
  "email": "john@example.com",
  "disabled": false
}
```

---

### 4. Get User's Items

```bash
curl -X GET "http://127.0.0.1:8000/users/me/items" \
  -H "Authorization: Bearer $TOKEN"
```

**Response:**
```json
{
  "user": "john",
  "items": [
    {"item_id": 1, "title": "Item One", "owner": "john"},
    {"item_id": 2, "title": "Item Two", "owner": "john"}
  ]
}
```

---

### 5. Test with Wrong Credentials

```bash
curl -X POST "http://127.0.0.1:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&password=wrongpassword"
```

**Response:**
```json
{
  "detail": "Incorrect username or password"
}
```

---

### 6. Test with Invalid Token

```bash
curl -X GET "http://127.0.0.1:8000/users/me" \
  -H "Authorization: Bearer invalid_token_here"
```

**Response:**
```json
{
  "detail": "Could not validate credentials"
}
```

---

### 7. Test Without Token

```bash
curl -X GET "http://127.0.0.1:8000/users/me"
```

**Response:**
```json
{
  "detail": "Not authenticated"
}
```

---

## 🐍 Using Python Requests

### Installation
```bash
pip install requests
```

### Complete Example Script

Create a file `test_api.py`:

```python
import requests
from datetime import datetime

# Base URL
BASE_URL = "http://127.0.0.1:8000"

def print_response(title, response):
    """Helper function to print formatted responses"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

def main():
    # 1. Get root information (public endpoint)
    print("\n1. Testing root endpoint (public)...")
    response = requests.get(f"{BASE_URL}/")
    print_response("Root Endpoint", response)
    
    # 2. Login and get token
    print("\n2. Logging in...")
    login_data = {
        "username": "john",
        "password": "secret"
    }
    response = requests.post(f"{BASE_URL}/token", data=login_data)
    print_response("Login", response)
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print(f"\nToken obtained: {token[:50]}...")
        
        # 3. Access protected endpoint with token
        print("\n3. Accessing protected endpoint with token...")
        headers = {"Authorization": f"Bearer {token}"}
        
        response = requests.get(f"{BASE_URL}/users/me", headers=headers)
        print_response("Get Current User", response)
        
        # 4. Get user's items
        print("\n4. Getting user's items...")
        response = requests.get(f"{BASE_URL}/users/me/items", headers=headers)
        print_response("Get User Items", response)
    
    # 5. Try with wrong credentials
    print("\n5. Testing with wrong credentials...")
    wrong_login = {
        "username": "john",
        "password": "wrongpassword"
    }
    response = requests.post(f"{BASE_URL}/token", data=wrong_login)
    print_response("Wrong Credentials", response)
    
    # 6. Try accessing protected endpoint without token
    print("\n6. Testing protected endpoint without token...")
    response = requests.get(f"{BASE_URL}/users/me")
    print_response("No Token", response)

if __name__ == "__main__":
    main()
```

### Run the script:
```bash
python test_api.py
```

---

## 🌐 Using JavaScript Fetch

### Complete HTML Example

Create a file `test_api.html`:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OAuth2 API Test</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
        }
        .section {
            margin: 20px 0;
            padding: 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px;
        }
        button:hover {
            background-color: #45a049;
        }
        .output {
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 4px;
            margin-top: 10px;
            white-space: pre-wrap;
            font-family: monospace;
        }
        input {
            padding: 8px;
            margin: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <h1>OAuth2 API Test</h1>
    
    <div class="section">
        <h2>1. Login</h2>
        <input type="text" id="username" placeholder="Username" value="john">
        <input type="password" id="password" placeholder="Password" value="secret">
        <button onclick="login()">Login</button>
        <div id="loginOutput" class="output"></div>
    </div>
    
    <div class="section">
        <h2>2. Get Current User</h2>
        <button onclick="getCurrentUser()">Get User Info</button>
        <div id="userOutput" class="output"></div>
    </div>
    
    <div class="section">
        <h2>3. Get User Items</h2>
        <button onclick="getUserItems()">Get Items</button>
        <div id="itemsOutput" class="output"></div>
    </div>

    <script>
        const BASE_URL = 'http://127.0.0.1:8000';
        let accessToken = null;

        // Login function
        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);
            
            try {
                const response = await fetch(`${BASE_URL}/token`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: formData
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    accessToken = data.access_token;
                    document.getElementById('loginOutput').textContent = 
                        `✅ Login successful!\nToken: ${accessToken.substring(0, 50)}...`;
                } else {
                    document.getElementById('loginOutput').textContent = 
                        `❌ Login failed: ${data.detail}`;
                }
            } catch (error) {
                document.getElementById('loginOutput').textContent = 
                    `❌ Error: ${error.message}`;
            }
        }

        // Get current user
        async function getCurrentUser() {
            if (!accessToken) {
                alert('Please login first!');
                return;
            }
            
            try {
                const response = await fetch(`${BASE_URL}/users/me`, {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
                
                const data = await response.json();
                document.getElementById('userOutput').textContent = 
                    JSON.stringify(data, null, 2);
            } catch (error) {
                document.getElementById('userOutput').textContent = 
                    `❌ Error: ${error.message}`;
            }
        }

        // Get user items
        async function getUserItems() {
            if (!accessToken) {
                alert('Please login first!');
                return;
            }
            
            try {
                const response = await fetch(`${BASE_URL}/users/me/items`, {
                    headers: {
                        'Authorization': `Bearer ${accessToken}`
                    }
                });
                
                const data = await response.json();
                document.getElementById('itemsOutput').textContent = 
                    JSON.stringify(data, null, 2);
            } catch (error) {
                document.getElementById('itemsOutput').textContent = 
                    `❌ Error: ${error.message}`;
            }
        }
    </script>
</body>
</html>
```

### Run:
1. Start the FastAPI server with CORS enabled (add to app.py):
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

2. Open `test_api.html` in your browser

---

## 📮 Using Postman

### Setup Collection

1. **Create a new collection** called "OAuth2 Tutorial"

2. **Add environment variables:**
   - `base_url`: `http://127.0.0.1:8000`
   - `token`: (leave empty, we'll set this automatically)

### Request 1: Login

- **Method**: POST
- **URL**: `{{base_url}}/token`
- **Body**: x-www-form-urlencoded
  - `username`: `john`
  - `password`: `secret`
- **Tests** (to auto-save token):
```javascript
const response = pm.response.json();
pm.environment.set("token", response.access_token);
```

### Request 2: Get Current User

- **Method**: GET
- **URL**: `{{base_url}}/users/me`
- **Authorization**: Bearer Token
  - Token: `{{token}}`

### Request 3: Get User Items

- **Method**: GET
- **URL**: `{{base_url}}/users/me/items`
- **Authorization**: Bearer Token
  - Token: `{{token}}`

---

## 🔍 Understanding the Flow

```
┌─────────┐                                  ┌─────────┐
│ Client  │                                  │  Server │
└────┬────┘                                  └────┬────┘
     │                                            │
     │  1. POST /token                           │
     │     (username, password)                  │
     ├──────────────────────────────────────────>│
     │                                            │
     │                                            │ 2. Verify credentials
     │                                            │    Create JWT token
     │                                            │
     │  3. Return token                          │
     │<──────────────────────────────────────────┤
     │                                            │
     │  4. GET /users/me                         │
     │     Authorization: Bearer <token>         │
     ├──────────────────────────────────────────>│
     │                                            │
     │                                            │ 5. Validate token
     │                                            │    Get user data
     │                                            │
     │  6. Return user data                      │
     │<──────────────────────────────────────────┤
     │                                            │
```

---

## 🎯 Quick Reference

### Test Users
| Username | Password |
|----------|----------|
| john     | secret   |
| jane     | secret   |

### Endpoints
| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| GET | / | ❌ No | API information |
| POST | /token | ❌ No | Login and get token |
| GET | /users/me | ✅ Yes | Get current user |
| GET | /users/me/items | ✅ Yes | Get user's items |

### Token Format
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 🐛 Common Errors

### 401 Unauthorized
- **Cause**: Invalid credentials or expired token
- **Solution**: Login again to get a fresh token

### 422 Unprocessable Entity
- **Cause**: Missing required fields or wrong format
- **Solution**: Check that username and password are sent as form data

### Not authenticated
- **Cause**: No Authorization header or missing "Bearer" prefix
- **Solution**: Include `Authorization: Bearer <token>` header

---

Happy testing! 🚀
