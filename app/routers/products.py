"""
Product API endpoints
Demonstrates GET, POST, PUT, DELETE operations with advanced filtering
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.schemas import ProductCreate, ProductUpdate, ProductResponse, MessageResponse
from app.crud import product as crud

router = APIRouter(
    prefix="/products",
    tags=["products"]
)


@router.get("/", response_model=List[ProductResponse])
def read_products(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search by name or description"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    in_stock: Optional[bool] = Query(None, description="Filter products in stock"),
    db: Session = Depends(get_db)
):
    """
    Get all products with advanced filtering
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 100)
    - **category**: Filter by product category
    - **search**: Search term for name or description
    - **min_price**: Minimum price filter
    - **max_price**: Maximum price filter
    - **in_stock**: Show only products in stock
    """
    products = crud.get_products(
        db, 
        skip=skip, 
        limit=limit, 
        category=category,
        search=search,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock
    )
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def read_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a single product by ID
    
    - **product_id**: The ID of the product to retrieve
    """
    db_product = crud.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return db_product


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new product
    
    - **name**: Product name (required)
    - **description**: Product description (optional)
    - **price**: Product price (required, must be positive)
    - **stock**: Initial stock quantity (default: 0)
    - **category**: Product category (optional)
    """
    return crud.create_product(db=db, product=product)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing product
    
    - **product_id**: The ID of the product to update
    - All fields are optional, only provided fields will be updated
    """
    db_product = crud.update_product(db, product_id=product_id, product=product)
    if db_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return db_product


@router.delete("/{product_id}", response_model=MessageResponse)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a product
    
    - **product_id**: The ID of the product to delete
    """
    success = crud.delete_product(db, product_id=product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with id {product_id} not found"
        )
    return MessageResponse(message=f"Product with id {product_id} deleted successfully")
