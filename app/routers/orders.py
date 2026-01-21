"""
Order API endpoints
Demonstrates complex operations with relationships and transactions
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.schemas import OrderCreate, OrderUpdate, OrderResponse, MessageResponse
from app.crud import order as crud

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)


@router.get("/", response_model=List[OrderResponse])
def read_orders(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    status: Optional[str] = Query(None, description="Filter by order status"),
    db: Session = Depends(get_db)
):
    """
    Get all orders with filtering
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    - **customer_id**: Filter by customer ID
    - **status**: Filter by order status (pending, completed, cancelled)
    """
    orders = crud.get_orders(
        db, 
        skip=skip, 
        limit=limit, 
        customer_id=customer_id,
        status=status
    )
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def read_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a single order by ID with all order items
    
    - **order_id**: The ID of the order to retrieve
    """
    db_order = crud.get_order(db, order_id=order_id)
    if db_order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )
    return db_order


@router.get("/customer/{customer_id}", response_model=List[OrderResponse])
def read_customer_orders(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all orders for a specific customer
    
    - **customer_id**: The ID of the customer
    """
    orders = crud.get_customer_orders(db, customer_id=customer_id)
    return orders


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new order with order items
    
    - **customer_id**: ID of the customer placing the order (required)
    - **items**: List of order items with product_id and quantity (required)
    
    This endpoint will:
    1. Validate that all products exist
    2. Check stock availability
    3. Create the order and order items
    4. Update product stock
    5. Calculate total amount
    """
    try:
        return crud.create_order(db=db, order=order)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order: OrderUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an order's status
    
    - **order_id**: The ID of the order to update
    - **status**: New status (pending, completed, cancelled)
    """
    if order.status:
        db_order = crud.update_order_status(db, order_id=order_id, status=order.status)
        if db_order is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Order with id {order_id} not found"
            )
        return db_order
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="No update data provided"
    )


@router.delete("/{order_id}", response_model=MessageResponse)
def delete_order(
    order_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an order
    
    - **order_id**: The ID of the order to delete
    """
    success = crud.delete_order(db, order_id=order_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order with id {order_id} not found"
        )
    return MessageResponse(message=f"Order with id {order_id} deleted successfully")
