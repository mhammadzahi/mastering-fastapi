"""
Pydantic schemas for request/response validation and serialization
Demonstrates data validation, type checking, and response models
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime


# ===== Customer Schemas =====

class CustomerBase(BaseModel):
    """Base schema with common customer fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Customer name")
    email: EmailStr = Field(..., description="Customer email address")
    phone: Optional[str] = Field(None, max_length=20, description="Customer phone number")
    address: Optional[str] = Field(None, description="Customer address")


class CustomerCreate(CustomerBase):
    """Schema for creating a new customer"""
    pass


class CustomerUpdate(BaseModel):
    """Schema for updating an existing customer (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None


class CustomerResponse(CustomerBase):
    """Schema for customer response with additional fields"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ===== Product Schemas =====

class ProductBase(BaseModel):
    """Base schema with common product fields"""
    name: str = Field(..., min_length=1, max_length=100, description="Product name")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., gt=0, description="Product price (must be positive)")
    stock: int = Field(default=0, ge=0, description="Available stock quantity")
    category: Optional[str] = Field(None, max_length=50, description="Product category")


class ProductCreate(ProductBase):
    """Schema for creating a new product"""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating an existing product (all fields optional)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, max_length=50)


class ProductResponse(ProductBase):
    """Schema for product response with additional fields"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ===== Order Schemas =====

class OrderItemBase(BaseModel):
    """Base schema for order items"""
    product_id: int = Field(..., gt=0, description="Product ID")
    quantity: int = Field(..., gt=0, description="Quantity to order")


class OrderItemCreate(OrderItemBase):
    """Schema for creating an order item"""
    pass


class OrderItemResponse(OrderItemBase):
    """Schema for order item response"""
    id: int
    price_at_time: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class OrderBase(BaseModel):
    """Base schema for orders"""
    customer_id: int = Field(..., gt=0, description="Customer ID")


class OrderCreate(OrderBase):
    """Schema for creating a new order with items"""
    items: List[OrderItemCreate] = Field(..., min_length=1, description="List of order items")


class OrderUpdate(BaseModel):
    """Schema for updating an order"""
    status: Optional[str] = Field(None, pattern="^(pending|completed|cancelled)$")


class OrderResponse(OrderBase):
    """Schema for order response"""
    id: int
    total_amount: float
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ===== Generic Response Schemas =====

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str


class ErrorResponse(BaseModel):
    """Error response schema"""
    detail: str
