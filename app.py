"""
FastAPI OAuth2 Complete Tutorial
=================================

This is a complete implementation of OAuth2 with JWT tokens in FastAPI.
Perfect for beginners learning authentication and authorization.

Key Concepts Covered:
1. Password hashing (bcrypt)
2. JWT token creation and validation
3. OAuth2 password bearer flow
4. Protected routes with dependencies
5. User authentication

Author: FastAPI OAuth2 Tutorial
"""

# Standard library imports
from datetime import datetime, timedelta

# Third-party imports
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext


# ==============================================================================
# APPLICATION SETUP
# ==============================================================================

app = FastAPI(
    title="OAuth2 Tutorial API",
    description="Learn OAuth2 authentication with FastAPI",
    version="1.0.0",
)


# ==============================================================================
# CONFIGURATION
# ==============================================================================

# SECRET_KEY: Used to encode/decode JWT tokens
# In production, use a strong random key and store it in environment variables!
# Generate one with: openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

# ALGORITHM: The algorithm used to sign the JWT
ALGORITHM = "HS256"

# ACCESS_TOKEN_EXPIRE_MINUTES: How long the token is valid
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# ==============================================================================
# PASSWORD HASHING SETUP
# ==============================================================================

# CryptContext: Handles password hashing using bcrypt
# bcrypt is a slow hashing algorithm designed to be computationally expensive
# This makes it resistant to brute-force attacks
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==============================================================================
# OAUTH2 SETUP
# ==============================================================================

# OAuth2PasswordBearer: Tells FastAPI to expect a Bearer token in the Authorization header
# tokenUrl="token": The URL where clients can get their token (our /token endpoint)
# When you use this in a dependency, FastAPI will:
# 1. Look for an Authorization header
# 2. Check if it has a Bearer token
# 3. Extract the token and pass it to your function
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ==============================================================================
# DATABASE (In-Memory)
# ==============================================================================

# In a real application, this would be a proper database (PostgreSQL, MySQL, etc.)
# For this tutorial, we use a simple dictionary
# Note: Passwords are pre-hashed using bcrypt
fake_users_db = {
    "john": {
        "username": "john",
        "full_name": "John Doe",
        "email": "john@example.com",
        "hashed_password": pwd_context.hash("secret"),  # Password: secret
        "disabled": False,
    },
    "jane": {
        "username": "jane",
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "hashed_password": pwd_context.hash("secret"),  # Password: secret
        "disabled": False,
    },
}


# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: The password provided by the user
        hashed_password: The hashed password from the database
    
    Returns:
        True if the password matches, False otherwise
    
    Example:
        >>> hashed = pwd_context.hash("mypassword")
        >>> verify_password("mypassword", hashed)
        True
        >>> verify_password("wrongpassword", hashed)
        False
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db: dict, username: str) -> dict:
    """
    Retrieve a user from the database by username.
    
    Args:
        db: The user database (dictionary)
        username: The username to look up
    
    Returns:
        User dictionary if found, None otherwise
    
    Example:
        >>> user = get_user(fake_users_db, "john")
        >>> print(user["full_name"])
        'John Doe'
    """
    return db.get(username)


def authenticate_user(username: str, password: str) -> dict:
    """
    Authenticate a user by verifying their username and password.
    
    This function:
    1. Looks up the user in the database
    2. Verifies the provided password against the stored hash
    3. Returns the user data if authentication succeeds
    
    Args:
        username: The username to authenticate
        password: The plain text password
    
    Returns:
        User dictionary if authentication succeeds, False otherwise
    
    Example:
        >>> user = authenticate_user("john", "secret")
        >>> if user:
        ...     print(f"Welcome {user['full_name']}!")
    """
    user = get_user(fake_users_db, username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    Create a JWT access token.
    
    JWT Structure: header.payload.signature
    - Header: Algorithm and token type
    - Payload: User data and expiration
    - Signature: Ensures the token hasn't been tampered with
    
    Args:
        data: Dictionary of data to encode in the token (e.g., {"sub": "username"})
        expires_delta: How long the token should be valid (optional)
    
    Returns:
        Encoded JWT token as a string
    
    Example:
        >>> token = create_access_token(
        ...     data={"sub": "john"},
        ...     expires_delta=timedelta(minutes=30)
        ... )
        >>> print(token)
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    
    Note:
        The "sub" (subject) field is a standard JWT claim for the subject of the token.
        In our case, it's the username.
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    # Add expiration to the token payload
    to_encode.update({"exp": expire})
    
    # Encode and sign the token
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



# ==============================================================================
# DEPENDENCY FUNCTIONS
# ==============================================================================

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Dependency function to get the current authenticated user.
    
    This function is used as a dependency in protected routes.
    It will:
    1. Extract the token from the Authorization header (via oauth2_scheme)
    2. Decode and validate the JWT token
    3. Extract the username from the token
    4. Look up and return the user from the database
    
    Args:
        token: JWT token extracted from Authorization header by oauth2_scheme
    
    Returns:
        User dictionary if token is valid
    
    Raises:
        HTTPException: If token is invalid, expired, or user not found
    
    Usage in routes:
        @app.get("/protected")
        async def protected_route(current_user: dict = Depends(get_current_user)):
            return {"message": f"Hello {current_user['username']}"}
    """
    # Define the exception to raise for authentication failures
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract the username from the "sub" (subject) claim
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
            
    except JWTError:
        # Token is invalid, expired, or malformed
        raise credentials_exception
    
    # Look up the user in the database
    user = get_user(fake_users_db, username)
    
    if user is None:
        raise credentials_exception
    
    return user


# ==============================================================================
# API ROUTES
# ==============================================================================

@app.get("/")
async def root():
    """
    Root endpoint - Public, no authentication required.
    
    Returns basic API information and instructions on how to get started.
    """
    return {
        "message": "Welcome to the OAuth2 Tutorial API!",
        "documentation": "/docs",
        "instructions": {
            "step_1": "Get a token from POST /token with username and password",
            "step_2": "Use the token in the Authorization header as 'Bearer <token>'",
            "step_3": "Access protected routes like GET /users/me",
        },
        "test_users": [
            {"username": "john", "password": "secret"},
            {"username": "jane", "password": "secret"},
        ],
    }


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 Token Endpoint - Login and get an access token.
    
    This is the endpoint where users exchange their credentials for a JWT access token.
    
    Flow:
    1. User sends username and password in a form
    2. Server authenticates the credentials
    3. If valid, server creates a JWT token
    4. Server returns the token to the user
    5. User uses this token for subsequent requests
    
    Args:
        form_data: Form containing username and password (automatically parsed by FastAPI)
    
    Returns:
        Dictionary with access_token and token_type
    
    Raises:
        HTTPException: If credentials are invalid (401 Unauthorized)
    
    Example Request (curl):
        curl -X POST "http://localhost:8000/token" \\
            -H "Content-Type: application/x-www-form-urlencoded" \\
            -d "username=john&password=secret"
    
    Example Response:
        {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "bearer"
        }
    """
    # Authenticate the user
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        # Authentication failed
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )
    
    # Return token in the format expected by OAuth2
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Protected endpoint - Get current user information.
    
    This endpoint requires authentication. The user must include a valid JWT token
    in the Authorization header.
    
    The Depends(get_current_user) tells FastAPI to:
    1. Call get_current_user function before executing this function
    2. Pass the result (user dict) as the current_user parameter
    3. If get_current_user raises an exception, return that error to the client
    
    Args:
        current_user: User dictionary injected by get_current_user dependency
    
    Returns:
        Current user's information
    
    Example Request (curl):
        curl -X GET "http://localhost:8000/users/me" \\
            -H "Authorization: Bearer <your_token_here>"
    
    Example Response:
        {
            "username": "john",
            "full_name": "John Doe",
            "email": "john@example.com",
            "disabled": false
        }
    """
    return current_user


@app.get("/users/me/items")
async def read_own_items(current_user: dict = Depends(get_current_user)):
    """
    Another protected endpoint - Get current user's items.
    
    This demonstrates how you can have multiple protected endpoints,
    all using the same authentication dependency.
    
    Args:
        current_user: User dictionary injected by get_current_user dependency
    
    Returns:
        Dictionary containing user info and their items
    """
    return {
        "user": current_user["username"],
        "items": [
            {"item_id": 1, "title": "Item One", "owner": current_user["username"]},
            {"item_id": 2, "title": "Item Two", "owner": current_user["username"]},
        ],
    }

