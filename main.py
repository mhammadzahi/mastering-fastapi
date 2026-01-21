"""
FastAPI Main Application
Integrates all routers, middleware, and database configuration
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.auth import AuthMiddleware
from app.routers import customers, products, orders
from app.database import engine, Base
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create database tables
# Note: In production, use Alembic for migrations
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="FastAPI Product & Customer Management API",
    description="A comprehensive API for managing customers, products, and orders with PostgreSQL",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ===== Configure CORS Middleware =====
# Allow requests from specific origins (configure for your needs)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# ===== Add Custom Middleware =====
# Order matters: middleware is executed in the order they are added
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthMiddleware)


# ===== Include Routers =====
app.include_router(customers.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(orders.router, prefix="/api")


# ===== Root Endpoint =====
@app.get("/")
def read_root():
    """
    Root endpoint with API information
    """
    return {
        "message": "Welcome to FastAPI Product & Customer Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "customers": "/api/customers",
            "products": "/api/products",
            "orders": "/api/orders"
        }
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}


# ===== Startup Event =====
@app.on_event("startup")
async def startup_event():
    """
    Actions to perform on application startup
    """
    logger.info("Starting FastAPI application...")
    logger.info("Database tables created/verified")


# ===== Shutdown Event =====
@app.on_event("shutdown")
async def shutdown_event():
    """
    Actions to perform on application shutdown
    """
    logger.info("Shutting down FastAPI application...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
