"""
Logging Middleware
Logs incoming requests and outgoing responses with timing information
"""
import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming requests and their processing time
    """
    async def dispatch(self, request: Request, call_next):
        # Log request
        logger.info(f"Incoming request: {request.method} {request.url.path}")
        logger.info(f"Client IP: {request.client.host}")
        
        # Start timer
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Time: {process_time:.4f}s"
        )
        
        # Add custom header with processing time
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
