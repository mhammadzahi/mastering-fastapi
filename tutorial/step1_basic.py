"""
Step 1: Basic FastAPI Application
==================================

In this first step, we'll create a simple FastAPI application with a few endpoints.
This forms the foundation before we add any authentication.

Learning Goals:
- Understand FastAPI basics
- Create simple GET endpoints
- Run the application with uvicorn
- View automatic API documentation

Run this file:
    uvicorn tutorial.step1_basic:app --reload

Then visit:
    http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI

# Create FastAPI application instance
app = FastAPI(
    title="Step 1: Basic API",
    description="A simple API without authentication",
    version="1.0.0",
)


@app.get("/")
async def root():
    """
    Root endpoint - returns a welcome message.
    
    This is a public endpoint that anyone can access.
    """
    return {
        "message": "Welcome to Step 1!",
        "description": "This is a basic FastAPI application",
        "next_step": "We'll add authentication in the next steps",
    }


@app.get("/public")
async def public_endpoint():
    """
    Another public endpoint.
    
    In a real application, some endpoints should be public (like a homepage),
    while others should be protected (like user profile).
    """
    return {
        "message": "This is a public endpoint",
        "accessible_by": "Everyone",
    }


@app.get("/users")
async def get_users():
    """
    Get list of users.
    
    Problem: Anyone can access this! 
    In the next steps, we'll protect endpoints like this.
    """
    return {
        "users": [
            {"username": "john", "full_name": "John Doe"},
            {"username": "jane", "full_name": "Jane Doe"},
        ]
    }


# ==============================================================================
# EXERCISE FOR YOU
# ==============================================================================
# Try adding your own endpoint! For example:
# 
# @app.get("/hello/{name}")
# async def hello(name: str):
#     return {"message": f"Hello {name}!"}
#
# Then test it at: http://127.0.0.1:8000/hello/YourName
# ==============================================================================
