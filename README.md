# 🔐 Mastering FastAPI OAuth2 - Complete Beginner's Guide

Welcome to the complete OAuth2 tutorial using FastAPI! This project will teach you how to implement secure authentication and authorization in your APIs step by step.

## 📚 Table of Contents

1. [What is OAuth2?](#what-is-oauth2)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Project Structure](#project-structure)
5. [Understanding the Code](#understanding-the-code)
6. [Running the Application](#running-the-application)
7. [Testing the API](#testing-the-api)
8. [Step-by-Step Tutorial](#step-by-step-tutorial)
9. [Common Issues](#common-issues)
10. [Next Steps](#next-steps)

---

## 🤔 What is OAuth2?

**OAuth2** is an authorization framework that allows applications to obtain limited access to user accounts. Think of it like a valet key for your car - it gives limited access without handing over your master key.

### Key Concepts:

- **Authentication**: Verifying who you are (like showing your ID)
- **Authorization**: Verifying what you can access (like checking your permissions)
- **Access Token**: A temporary key that grants access to protected resources
- **Bearer Token**: A type of access token that anyone holding it can use (like a concert ticket)

### OAuth2 Flow in This Tutorial:

```
1. User sends username + password → /token endpoint
2. Server verifies credentials
3. Server creates JWT (JSON Web Token)
4. Server returns token to user
5. User includes token in subsequent requests
6. Server validates token and grants access
```

---

## 📋 Prerequisites

Before starting, you should have:

- **Python 3.8+** installed
- Basic understanding of:
  - Python programming
  - HTTP requests (GET, POST)
  - APIs and REST concepts
  - Command line/terminal basics

---

## 🚀 Installation

### Step 1: Create a Virtual Environment

A virtual environment keeps your project dependencies isolated.

```bash
# Create virtual environment
python -m venv env

# Activate it
# On Linux/Mac:
source env/bin/activate
# On Windows:
env\Scripts\activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **fastapi**: The web framework
- **uvicorn**: ASGI server to run the app
- **python-jose**: JWT token creation/validation
- **passlib**: Password hashing
- **python-multipart**: Form data handling
- **python-dotenv**: Environment variable management

### Step 3: Setup Environment Variables

```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and customize your settings (optional)
# The defaults work fine for learning
nano .env  # or use your favorite editor
```

**Important**: Never commit `.env` to version control! It contains secrets.

### Step 4: Initialize the Database

```bash
# Create the SQLite database and add sample users
python init_db.py
```

This creates:
- `users.db` - SQLite database file
- Sample users: john, jane, admin (password: see output)

---

## 📁 Project Structure

```
mastering-fastapi/
├── app.py              # Main application (fully implemented)
├── database.py         # SQLite database operations
├── init_db.py          # Database initialization script
├── requirements.txt    # Python dependencies
├── .env                # Environment variables (SECRET_KEY, etc.)
├── .env.example        # Example environment file
├── .gitignore          # Git ignore rules
├── users.db            # SQLite database (created by init_db.py)
├── README.md          # This tutorial
├── API_EXAMPLES.md    # API usage examples
├── tutorial/          # Step-by-step learning files
│   ├── step1_basic.py
│   ├── step2_password_hashing.py
│   ├── step3_jwt_tokens.py
│   └── step4_complete.py
└── env/               # Virtual environment (created by you)
```

---

## 🧠 Understanding the Code

### 1. Environment Variables (.env file)

**Why?** Store sensitive configuration like SECRET_KEY outside your code!

```bash
# .env file
SECRET_KEY=your-secret-key-here
DATABASE_URL=./users.db
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

In Python:
```python
from dotenv import load_dotenv
import os

load_dotenv()  # Load .env file
SECRET_KEY = os.getenv("SECRET_KEY")
```

### 2. SQLite Database

**Why?** Store users persistently, not just in memory!

```python
from database import get_database

db = get_database()  # Connect to SQLite
user = db.get_user("john")  # Query the database
```

### 3. Password Hashing

**Why?** Never store passwords in plain text! If your database is compromised, hashed passwords are useless to attackers.

```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed = pwd_context.hash("secret")  # Create hash
verified = pwd_context.verify("secret", hashed)  # Verify password
```

### 4. JWT Tokens (JSON Web Tokens)

**What?** JWTs are encoded JSON objects that contain claims (user data) and are digitally signed.

**Structure**: `header.payload.signature`

```python
# Creating a token
token = jwt.encode(
    {"sub": "username", "exp": expiration_time},
    SECRET_KEY,
    algorithm="HS256"
)

# Decoding a token
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

### 5. OAuth2 Password Bearer

**What?** A scheme where the client sends credentials once, receives a token, then uses that token for subsequent requests.

```python
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
# This tells FastAPI where to get the token (/token endpoint)
```

### 6. Protected Routes

Use `Depends()` to require authentication:

```python
@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user
```

---

## 🏃 Running the Application

### Start the Server

```bash
uvicorn app:app --reload
```

**Flags explained:**
- `app:app` - module:instance (file "app.py", FastAPI instance "app")
- `--reload` - Auto-restart when code changes (development only)

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Access the Interactive Docs

Open your browser and visit:

- **Swagger UI**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

The Swagger UI provides an interactive interface to test all endpoints!

---

## 🧪 Testing the API

### Method 1: Using Swagger UI (Easiest)

1. Go to http://127.0.0.1:8000/docs
2. Click on `/token` endpoint
3. Click "Try it out"
4. Enter credentials:
   - **username**: `john`
   - **password**: `secret`
5. Click "Execute"
6. Copy the `access_token` from the response
7. Click the "Authorize" button at the top
8. Paste the token and click "Authorize"
9. Now try the `/users/me` endpoint!

### Method 2: Using curl (Command Line)

See [API_EXAMPLES.md](API_EXAMPLES.md) for detailed curl commands.

### Method 3: Using Python Requests

```python
import requests

# Step 1: Get token
response = requests.post(
    "http://127.0.0.1:8000/token",
    data={"username": "john", "password": "secret"}
)
token = response.json()["access_token"]

# Step 2: Use token
response = requests.get(
    "http://127.0.0.1:8000/users/me",
    headers={"Authorization": f"Bearer {token}"}
)
print(response.json())
```

---

## 📖 Step-by-Step Tutorial

Learn OAuth2 progressively by following the tutorial files in order:

### Step 1: Basic API (`tutorial/step1_basic.py`)
- Create a simple FastAPI app
- Add a public endpoint
- Understand the basics

### Step 2: Password Hashing (`tutorial/step2_password_hashing.py`)
- Add user database
- Implement password hashing with bcrypt
- Create authentication function

### Step 3: JWT Tokens (`tutorial/step3_jwt_tokens.py`)
- Generate JWT access tokens
- Create login endpoint
- Return tokens to users

### Step 4: Complete OAuth2 (`tutorial/step4_complete.py`)
- Add OAuth2 password bearer scheme
- Create protected endpoints
- Implement token validation
- Full working example

Each file builds on the previous one and includes detailed comments explaining every concept.

---

## ❓ Common Issues

### Issue: "ModuleNotFoundError"
**Solution**: Make sure your virtual environment is activated and dependencies are installed:
```bash
source env/bin/activate  # or env\Scripts\activate on Windows
pip install -r requirements.txt
```

### Issue: "Database not found"
**Solution**: Initialize the database:
```bash
python init_db.py
```

### Issue: "401 Unauthorized"
**Solution**: 
- Check username/password (run `python init_db.py` to see credentials)
- Ensure token is prefixed with "Bearer " in Authorization header
- Verify token hasn't expired (default: 30 minutes)

### Issue: "Token expired"
**Solution**: Request a new token from `/token` endpoint

### Issue: "Invalid credentials"
**Solution**: 
- Token might be malformed
- SECRET_KEY might have changed
- Token might be from a different server instance

---

## 🎯 Next Steps

Now that you understand OAuth2 basics, here are ways to improve:

### Security Enhancements:
1. **Use Strong SECRET_KEY**: Generate with `openssl rand -hex 32`
   ```python
   # Already done! Check your .env file
   SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
   ```

2. **Never Commit .env**: Already in .gitignore!

2. **Never Commit .env**: Already in .gitignore!

3. **Refresh Tokens**: Add long-lived refresh tokens alongside access tokens

4. **Token Blacklisting**: Implement logout by blacklisting tokens

5. **Rate Limiting**: Prevent brute force attacks on login

6. **HTTPS Only**: Never use OAuth2 without HTTPS in production

### Database Improvements:
1. **Migrate to PostgreSQL**: For production use
   ```bash
   # Update DATABASE_URL in .env
   DATABASE_URL=postgresql://user:pass@localhost/dbname
   ```

2. **Add Migrations**: Use Alembic for database schema changes

3. **Connection Pooling**: For better performance

### User Management:
1. Replace `fake_users_db` with a real database (PostgreSQL, MySQL)
2. Use SQLAlchemy ORM for database operations
3. Add user registration endpoint

### Advanced Features:
1. **User Roles**: Add role-based access control (RBAC)
2. **Scopes**: Implement OAuth2 scopes for fine-grained permissions
3. **Multi-Factor Authentication**: Add 2FA/MFA support
4. **OAuth2 Providers**: Allow login with Google, GitHub, etc.

### Production Deployment:
1. Use a production ASGI server (Gunicorn + Uvicorn workers)
2. Set up environment-based configuration
3. Add logging and monitoring
4. Use a reverse proxy (Nginx)
5. Deploy to cloud (AWS, GCP, Heroku, DigitalOcean)

---

## 📚 Additional Resources

### Official Documentation:
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [OAuth2 Specification](https://oauth.net/2/)
- [JWT.io](https://jwt.io/) - Decode and verify JWTs

### Recommended Reading:
- FastAPI documentation: https://fastapi.tiangolo.com
- OAuth2 Simplified: https://aaronparecki.com/oauth-2-simplified/
- Password Hashing: https://passlib.readthedocs.io/

---

## 🤝 Contributing

Found an issue or want to improve this tutorial? Contributions are welcome!

---

## 📄 License

This tutorial is provided as-is for educational purposes.

---

## 🎓 Summary

You've learned:
- ✅ What OAuth2 is and why it's important
- ✅ How to use environment variables for configuration
- ✅ How to use SQLite database for persistent storage
- ✅ How to hash passwords securely
- ✅ How to create and validate JWT tokens
- ✅ How to implement OAuth2 password flow in FastAPI
- ✅ How to protect routes with authentication
- ✅ How to test authenticated endpoints

**Happy coding! 🚀**
