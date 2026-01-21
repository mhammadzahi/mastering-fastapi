"""
Step 4: Complete OAuth2 Implementation
=======================================

This is the complete OAuth2 implementation with all concepts combined!

Learning Goals:
- Use OAuth2PasswordBearer for token extraction
- Protect routes with authentication dependencies
- Implement the complete OAuth2 password flow
- Understand how everything works together

This is the same as the main app.py but with extensive comments for learning.

Run this file:
    uvicorn tutorial.step4_complete:app --reload
    
Then test at:
    http://127.0.0.1:8000/docs
"""

from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

# ==============================================================================
# APPLICATION SETUP
# ==============================================================================

app = FastAPI(
    title="Step 4: Complete OAuth2",
    description="Full OAuth2 implementation with protected routes",
    version="1.0.0",
)

# ==============================================================================
# CONFIGURATION
# ==============================================================================

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ==============================================================================
# OAUTH2 SETUP - THE KEY ADDITION!
# ==============================================================================

# OAuth2PasswordBearer: This is what makes routes protected!
# It tells FastAPI:
# 1. Look for "Authorization: Bearer <token>" header
# 2. Extract the token
# 3. Pass it to dependency functions
# 4. If no token is found, automatically return 401 Unauthorized
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# The magic of Depends(oauth2_scheme):
# - When you use it in a route, FastAPI automatically checks for the token
# - If token is missing: Returns 401 immediately
# - If token is present: Passes it to your function


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
# UTILITY FUNCTIONS
# ==============================================================================

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_user(username: str):
    """Get user from database"""
    return users_db.get(username)


def authenticate_user(username: str, password: str):
    """Authenticate user credentials"""
    user = get_user(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ==============================================================================
# DEPENDENCY: Get Current User
# ==============================================================================

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """
    THE CORE DEPENDENCY FUNCTION!
    
    This function is called automatically by FastAPI when you use:
        Depends(get_current_user)
    
    Flow:
    1. oauth2_scheme extracts token from Authorization header
    2. This function receives the token
    3. Decode and validate the token
    4. Look up the user
    5. Return user data
    
    If anything fails, raise HTTPException(401)
    
    Usage in routes:
        @app.get("/protected")
        async def protected(user: dict = Depends(get_current_user)):
            # user is automatically injected here!
            return user
    """
    # Define error to raise if authentication fails
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            print("❌ Token has no 'sub' claim")
            raise credentials_exception
        
        print(f"✅ Token decoded: user={username}")
        
    except JWTError as e:
        print(f"❌ JWT Error: {e}")
        raise credentials_exception
    
    # Look up user in database
    user = get_user(username)
    if user is None:
        print(f"❌ User {username} not found in database")
        raise credentials_exception
    
    print(f"✅ User {username} authenticated")
    return user


# ==============================================================================
# OPTIONAL: Get current active user
# ==============================================================================

async def get_current_active_user(
    current_user: dict = Depends(get_current_user)
) -> dict:
    """
    Optional additional dependency layer.
    
    This shows how you can chain dependencies!
    - First, get_current_user runs (validates token)
    - Then, this function runs (checks if user is active)
    
    This is useful for:
    - Checking if user is disabled/banned
    - Checking user permissions
    - Checking subscription status
    - etc.
    """
    if current_user.get("disabled", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


# ==============================================================================
# PUBLIC ROUTES (No authentication required)
# ==============================================================================

@app.get("/")
async def root():
    """
    Public endpoint - no authentication required.
    
    Notice: No Depends() parameter, so anyone can access this.
    """
    return {
        "message": "Welcome to Step 4: Complete OAuth2!",
        "public_endpoints": ["/", "/docs"],
        "protected_endpoints": ["/users/me", "/users/me/items", "/admin"],
        "instructions": {
            "1": "POST /token with username and password to get a token",
            "2": "Click 'Authorize' button in /docs and paste your token",
            "3": "Try accessing the protected endpoints",
        },
    }


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 token endpoint.
    
    OAuth2PasswordRequestForm automatically parses:
    - username (from form field)
    - password (from form field)
    
    This endpoint is PUBLIC (anyone can try to login).
    """
    # Authenticate
    user = authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )
    
    print(f"✅ User {user['username']} logged in successfully")
    
    # Return token
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# ==============================================================================
# PROTECTED ROUTES (Authentication required)
# ==============================================================================

@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    PROTECTED endpoint - requires authentication.
    
    The magic happens here:
    1. Client sends: Authorization: Bearer <token>
    2. oauth2_scheme extracts the token
    3. get_current_user validates token and fetches user
    4. If successful, current_user contains the user data
    5. If failed, 401 error is returned automatically
    
    Try accessing this WITHOUT a token - you'll get 401!
    """
    print(f"📊 GET /users/me called by {current_user['username']}")
    return current_user


@app.get("/users/me/items")
async def read_own_items(current_user: dict = Depends(get_current_user)):
    """
    Another PROTECTED endpoint.
    
    Same dependency, different route.
    Shows how you can reuse get_current_user for any protected route.
    """
    print(f"📊 GET /users/me/items called by {current_user['username']}")
    return {
        "user": current_user["username"],
        "items": [
            {"id": 1, "title": "My Item 1", "description": "First item"},
            {"id": 2, "title": "My Item 2", "description": "Second item"},
        ],
    }


@app.get("/admin")
async def admin_route(current_user: dict = Depends(get_current_active_user)):
    """
    PROTECTED endpoint with additional checks.
    
    Uses get_current_active_user which:
    1. Validates token (via get_current_user)
    2. Checks if user is active
    
    In a real app, you could add more checks here:
    - Check if user has "admin" role
    - Check if user has specific permissions
    - Check if user's subscription is active
    """
    print(f"🔐 GET /admin called by {current_user['username']}")
    return {
        "message": "Welcome to the admin area!",
        "user": current_user["username"],
        "note": "In a real app, you'd check for admin role here",
    }


# ==============================================================================
# DEMONSTRATION: Compare Public vs Protected
# ==============================================================================

@app.get("/public/data")
async def public_data():
    """
    Public endpoint - no authentication.
    
    Compare this to the protected endpoint below.
    """
    return {
        "data": "This is public data",
        "accessible_by": "Everyone",
    }


@app.get("/protected/data")
async def protected_data(current_user: dict = Depends(get_current_user)):
    """
    Protected endpoint - requires authentication.
    
    Notice the only difference is: Depends(get_current_user)
    That one parameter makes this route protected!
    """
    return {
        "data": "This is protected data",
        "accessible_by": "Authenticated users only",
        "accessed_by": current_user["username"],
    }


# ==============================================================================
# UNDERSTANDING THE FLOW
# ==============================================================================
"""
COMPLETE OAUTH2 FLOW:

1. CLIENT LOGS IN:
   POST /token
   Body: username=john&password=secret
   
2. SERVER VALIDATES:
   - authenticate_user() checks credentials
   - create_access_token() creates JWT
   
3. SERVER RESPONDS:
   {
     "access_token": "eyJhbGci...",
     "token_type": "bearer"
   }
   
4. CLIENT STORES TOKEN:
   - In memory, localStorage, or secure cookie
   
5. CLIENT ACCESSES PROTECTED ROUTE:
   GET /users/me
   Header: Authorization: Bearer eyJhbGci...
   
6. SERVER VALIDATES TOKEN:
   - oauth2_scheme extracts token from header
   - get_current_user() decodes and validates token
   - get_current_user() returns user data
   
7. SERVER RESPONDS:
   {
     "username": "john",
     "full_name": "John Doe",
     ...
   }

IF TOKEN IS MISSING OR INVALID:
   - oauth2_scheme returns 401 Unauthorized
   - Client must login again

IF TOKEN IS EXPIRED:
   - jwt.decode() raises JWTError
   - get_current_user() raises HTTPException(401)
   - Client must login again
"""


# ==============================================================================
# EXERCISE FOR YOU
# ==============================================================================
# Try these experiments:
#
# 1. Visit http://127.0.0.1:8000/docs
#
# 2. Try accessing GET /users/me without authentication
#    - You'll get 401 Unauthorized
#
# 3. Login via POST /token
#    - Username: john
#    - Password: secret
#
# 4. Click the "Authorize" button and paste your token
#
# 5. Now try GET /users/me again
#    - Success! You'll see your user data
#
# 6. Compare /public/data vs /protected/data
#    - One works without auth, one doesn't
#
# 7. Try the /admin endpoint
#
# 8. Wait 30 minutes and try again
#    - Your token will be expired!
#
# CONGRATULATIONS! 🎉
# You now understand OAuth2 with JWT tokens in FastAPI!
#
# Next steps:
# - Add user registration
# - Implement refresh tokens
# - Add role-based access control (RBAC)
# - Connect to a real database
# - Deploy to production with HTTPS
# ==============================================================================
