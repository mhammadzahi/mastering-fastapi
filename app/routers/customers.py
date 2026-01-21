"""
Customer API endpoints
Demonstrates GET, POST, PUT, DELETE operations with FastAPI
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.schemas import CustomerCreate, CustomerUpdate, CustomerResponse, MessageResponse
from app.crud import customer as crud

router = APIRouter(
    prefix="/customers",
    tags=["customers"]
)


@router.get("/", response_model=List[CustomerResponse])
def read_customers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Search by name or email"),
    db: Session = Depends(get_db)
):
    """
    Get all customers with pagination and optional search
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    - **search**: Search term for name or email
    """
    customers = crud.get_customers(db, skip=skip, limit=limit, search=search)
    return customers


@router.get("/{customer_id}", response_model=CustomerResponse)
def read_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a single customer by ID
    
    - **customer_id**: The ID of the customer to retrieve
    """
    db_customer = crud.get_customer(db, customer_id=customer_id)
    if db_customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id {customer_id} not found"
        )
    return db_customer


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new customer
    
    - **name**: Customer name (required)
    - **email**: Customer email address (required, must be unique)
    - **phone**: Customer phone number (optional)
    - **address**: Customer address (optional)
    """
    # Check if email already exists
    db_customer = crud.get_customer_by_email(db, email=customer.email)
    if db_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    return crud.create_customer(db=db, customer=customer)


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing customer
    
    - **customer_id**: The ID of the customer to update
    - All fields are optional, only provided fields will be updated
    """
    db_customer = crud.update_customer(db, customer_id=customer_id, customer=customer)
    if db_customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id {customer_id} not found"
        )
    return db_customer


@router.delete("/{customer_id}", response_model=MessageResponse)
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a customer
    
    - **customer_id**: The ID of the customer to delete
    """
    success = crud.delete_customer(db, customer_id=customer_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with id {customer_id} not found"
        )
    return MessageResponse(message=f"Customer with id {customer_id} deleted successfully")
