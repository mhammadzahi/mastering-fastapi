"""
Step 2: Password Hashing
=========================

In this step, we add user management with secure password hashing.

Learning Goals:
- Store users in a database (using a dictionary for simplicity)
- Hash passwords using bcrypt
- Never store plain text passwords
- Authenticate users by verifying passwords

Key Concept: Password Hashing
------------------------------
Hashing is a one-way function: plain_password -> hash
You can't reverse it: hash -> plain_password (impossible!)

But you CAN verify: Does "secret" match this hash? (Yes/No)

Run this file:
    uvicorn tutorial.step2_password_hashing:app --reload
"""

from fastapi import FastAPI, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel

# Create FastAPI application
app = FastAPI(
    title="Step 2: Password Hashing",
    description="Learning secure password storage",
    version="1.0.0",
)

# ==============================================================================
# PASSWORD HASHING SETUP
# ==============================================================================

# CryptContext manages password hashing
# bcrypt is slow by design - this makes brute force attacks impractical
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==============================================================================
# DATABASE (In-Memory)
# ==============================================================================

# In a real app, this would be a database
# Note: We're storing HASHED passwords, not plain text
users_db = {
    "john": {
        "username": "john",
        "full_name": "John Doe",
        "email": "john@example.com",
        "hashed_password": pwd_context.hash("secret"),  # Plain password: "secret"
    },
    "jane": {
        "username": "jane",
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "hashed_password": pwd_context.hash("secret"),  # Plain password: "secret"
    },
}


# ==============================================================================
# REQUEST/RESPONSE MODELS
# ==============================================================================

class LoginRequest(BaseModel):
    """Model for login request data"""
    username: str
    password: str


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Example:
        >>> hashed = pwd_context.hash("mypassword")
        >>> verify_password("mypassword", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str):
    """Retrieve a user from the database"""
    return users_db.get(username)


def authenticate_user(username: str, password: str):
    """
    Authenticate a user.
    
    Steps:
    1. Look up user in database
    2. Verify password matches the stored hash
    3. Return user if successful, False otherwise
    """
    user = get_user(username)
    
    if not user:
        print(f"❌ User '{username}' not found")
        return False
    
    if not verify_password(password, user["hashed_password"]):
        print(f"❌ Invalid password for user '{username}'")
        return False
    
    print(f"✅ User '{username}' authenticated successfully")
    return user


# ==============================================================================
# API ROUTES
# ==============================================================================

@app.get("/")
async def root():
    """Root endpoint with instructions"""
    return {
        "message": "Welcome to Step 2: Password Hashing!",
        "instructions": "Try the POST /login endpoint with username and password",
        "test_credentials": {
            "username": "john",
            "password": "secret",
        },
    }


@app.post("/login")
async def login(login_data: LoginRequest):
    """
    Login endpoint - authenticate user with username and password.
    
    This demonstrates password verification but doesn't issue tokens yet.
    We'll add tokens in the next step!
    """
    user = authenticate_user(login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    # Success! In the next step, we'll return a JWT token instead
    return {
        "message": f"Welcome back, {user['full_name']}!",
        "user": {
            "username": user["username"],
            "full_name": user["full_name"],
            "email": user["email"],
        },
        "note": "In the next step, we'll return a JWT token instead of user data",
    }


@app.get("/users/{username}")
async def get_user_info(username: str):
    """
    Get user information.
    
    Problem: Anyone can access any user's information!
    We'll fix this in Step 4 by requiring authentication.
    """
    user = get_user(username)
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )
    
    # Don't return the hashed password!
    return {
        "username": user["username"],
        "full_name": user["full_name"],
        "email": user["email"],
    }


# ==============================================================================
# DEMONSTRATION: Password Hashing
# ==============================================================================

@app.get("/demo/hash/{password}")
async def demo_hashing(password: str):
    """
    Demonstration endpoint: Hash a password and verify it.
    
    Try: GET /demo/hash/mypassword
    
    This shows you how hashing works:
    - Same password always produces different hashes (due to salt)
    - But verification still works!
    """
    hash1 = pwd_context.hash(password)
    hash2 = pwd_context.hash(password)
    
    return {
        "original_password": password,
        "hash_1": hash1,
        "hash_2": hash2,
        "note": "Notice the hashes are different, but both can verify the password!",
        "verification": {
            "hash1_valid": pwd_context.verify(password, hash1),
            "hash2_valid": pwd_context.verify(password, hash2),
            "wrong_password": pwd_context.verify("wrong", hash1),
        },
    }


# ==============================================================================
# EXERCISE FOR YOU
# ==============================================================================
# Try these experiments:
#
# 1. Test with correct credentials:
#    POST /login with {"username": "john", "password": "secret"}
#
# 2. Test with wrong password:
#    POST /login with {"username": "john", "password": "wrong"}
#
# 3. Try the hash demo:
#    GET /demo/hash/test123
#    Notice how the same password produces different hashes!
#
# 4. Think about: Why is this more secure than storing plain passwords?
# ==============================================================================
