"""
Authentication Middleware Placeholder
Demonstrates a simple authentication check (placeholder implementation)
In production, implement proper JWT token validation or OAuth2
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Simple authentication middleware placeholder
    In production, implement proper token validation
    """
    
    # Public paths that don't require authentication
    PUBLIC_PATHS = [
        "/",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/health"
    ]
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for public paths
        if any(request.url.path.startswith(path) for path in self.PUBLIC_PATHS):
            return await call_next(request)
        
        # Check for API key in header (placeholder implementation)
        api_key = request.headers.get("X-API-Key")
        
        if not api_key:
            logger.warning(f"Unauthorized access attempt to {request.url.path}")
            # In this placeholder, we'll just log and continue
            # In production, uncomment the following to enforce authentication:
            # raise HTTPException(
            #     status_code=status.HTTP_401_UNAUTHORIZED,
            #     detail="API Key required"
            # )
        
        # Validate API key (placeholder - in production, validate against database)
        # For demo purposes, we accept any API key
        if api_key:
            logger.info(f"Authenticated request with API key: {api_key[:8]}...")
        
        response = await call_next(request)
        return response


# Placeholder function for future JWT token validation
def verify_token(token: str) -> dict:
    """
    Placeholder for JWT token verification
    In production, implement proper JWT validation
    
    Example implementation:
    ```python
    from jose import JWTError, jwt
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    ```
    """
    pass


# Placeholder function for password hashing
def get_password_hash(password: str) -> str:
    """
    Placeholder for password hashing
    In production, use passlib or bcrypt
    
    Example implementation:
    ```python
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.hash(password)
    ```
    """
    pass


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Placeholder for password verification
    In production, use passlib or bcrypt
    
    Example implementation:
    ```python
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)
    ```
    """
    pass
