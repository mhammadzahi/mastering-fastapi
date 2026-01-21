"""
Step 3: JWT Tokens
==================

In this step, we add JWT (JSON Web Token) generation.

Learning Goals:
- Understand what JWT tokens are
- Create JWT tokens after successful authentication
- Decode and validate JWT tokens
- Understand token expiration

Key Concept: JWT (JSON Web Token)
----------------------------------
A JWT is a string with three parts separated by dots:

    header.payload.signature
    
Example:
    eyJhbGci...  .  eyJzdWIi...  .  SflKxwRJ...
    ^header         ^payload        ^signature

- Header: Token type and algorithm
- Payload: User data (claims) like username, expiration
- Signature: Ensures the token hasn't been tampered with

Run this file:
    uvicorn tutorial.step3_jwt_tokens:app --reload
"""

from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel
from jose import JWTError, jwt

# Create FastAPI application
app = FastAPI(
    title="Step 3: JWT Tokens",
    description="Learning JWT token creation and validation",
    version="1.0.0",
)

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# SECRET_KEY: Used to sign and verify JWTs
# IMPORTANT: In production, use a strong random key and store in environment variables!
# Generate with: openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"  # Algorithm for signing tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token lifetime

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==============================================================================
# DATABASE
# ==============================================================================

users_db = {
    "john": {
        "username": "john",
        "full_name": "John Doe",
        "email": "john@example.com",
        "hashed_password": pwd_context.hash("secret"),
    },
    "jane": {
        "username": "jane",
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "hashed_password": pwd_context.hash("secret"),
    },
}


# ==============================================================================
# REQUEST/RESPONSE MODELS
# ==============================================================================

class LoginRequest(BaseModel):
    """Login request with username and password"""
    username: str
    password: str


class Token(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str):
    """Get user from database"""
    return users_db.get(username)


def authenticate_user(username: str, password: str):
    """Authenticate user with username and password"""
    user = get_user(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary with user data (usually {"sub": username})
        expires_delta: How long the token is valid
    
    Returns:
        Encoded JWT token string
    
    JWT Structure:
        {
            "sub": "john",           # Subject (username)
            "exp": 1706205600        # Expiration timestamp
        }
    """
    to_encode = data.copy()
    
    # Calculate expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    # Add expiration to the token payload
    to_encode.update({"exp": expire})
    
    # Create and sign the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    print(f"✅ Created token for user: {data.get('sub')}")
    print(f"   Expires at: {expire}")
    
    return encoded_jwt


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload dictionary
    
    Raises:
        JWTError: If token is invalid or expired
    """
    try:
        # Decode and verify the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"✅ Token decoded successfully")
        print(f"   Subject: {payload.get('sub')}")
        print(f"   Expires: {datetime.fromtimestamp(payload.get('exp'))}")
        return payload
    except JWTError as e:
        print(f"❌ Token validation failed: {e}")
        raise


# ==============================================================================
# API ROUTES
# ==============================================================================

@app.get("/")
async def root():
    """Root endpoint with instructions"""
    return {
        "message": "Welcome to Step 3: JWT Tokens!",
        "instructions": [
            "1. POST /login to get a JWT token",
            "2. POST /validate to check if a token is valid",
            "3. GET /demo/token to see how tokens are created",
        ],
        "test_credentials": {
            "username": "john",
            "password": "secret",
        },
    }


@app.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    """
    Login endpoint - returns a JWT token.
    
    Flow:
    1. Authenticate username and password
    2. Create JWT token with username
    3. Return token to client
    
    The client should store this token and include it in future requests.
    """
    # Authenticate user
    user = authenticate_user(login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},  # "sub" is the standard claim for subject
        expires_delta=access_token_expires
    )
    
    # Return token
    return {
        "access_token": access_token,
        "token_type": "bearer",  # OAuth2 standard token type
    }


@app.post("/validate")
async def validate_token(token: str):
    """
    Validate a JWT token and show its contents.
    
    Try this:
    1. Get a token from POST /login
    2. Send it to POST /validate
    3. See the decoded payload
    """
    try:
        # Decode the token
        payload = decode_token(token)
        
        # Extract information
        username = payload.get("sub")
        exp_timestamp = payload.get("exp")
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        time_remaining = exp_datetime - datetime.utcnow()
        
        return {
            "valid": True,
            "username": username,
            "expires_at": exp_datetime.isoformat(),
            "time_remaining": str(time_remaining),
            "full_payload": payload,
        }
    
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )


@app.get("/demo/token")
async def demo_token():
    """
    Demonstration: Create a token and decode it.
    
    This shows you exactly what's inside a JWT token!
    """
    # Create a token
    token = create_access_token(
        data={"sub": "demo_user", "role": "admin"},
        expires_delta=timedelta(minutes=30)
    )
    
    # Decode it to show contents
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    # Split token into parts
    parts = token.split('.')
    
    return {
        "token": token,
        "token_parts": {
            "header": parts[0],
            "payload": parts[1],
            "signature": parts[2],
        },
        "decoded_payload": payload,
        "explanation": {
            "sub": "Subject - the user this token is for",
            "exp": "Expiration - when this token expires (Unix timestamp)",
            "role": "Custom claim - you can add any data you want",
        },
        "note": "Copy the token and paste it at jwt.io to see it decoded!",
    }


@app.get("/demo/expired")
async def demo_expired_token():
    """
    Demonstration: Create an already-expired token.
    
    This shows what happens when you try to use an expired token.
    """
    # Create a token that expired 1 minute ago
    token = create_access_token(
        data={"sub": "demo_user"},
        expires_delta=timedelta(minutes=-1)  # Negative = already expired!
    )
    
    # Try to decode it
    try:
        payload = decode_token(token)
        return {"status": "This shouldn't happen!"}
    except JWTError as e:
        return {
            "token": token,
            "error": str(e),
            "explanation": "This token is expired, so decoding fails",
            "note": "In a real app, the user would need to login again",
        }


# ==============================================================================
# EXERCISE FOR YOU
# ==============================================================================
# Try these experiments:
#
# 1. Login and get a token:
#    POST /login with {"username": "john", "password": "secret"}
#
# 2. Validate your token:
#    POST /validate with the token you received
#
# 3. Try the demo:
#    GET /demo/token
#    Copy the token and paste it at https://jwt.io/ to decode it
#
# 4. See what expired tokens look like:
#    GET /demo/expired
#
# 5. Think about: 
#    - What happens if someone modifies the token?
#    - How does the signature prevent tampering?
#    - Why do tokens expire?
#
# Next Step: In Step 4, we'll use these tokens to protect API endpoints!
# ==============================================================================
