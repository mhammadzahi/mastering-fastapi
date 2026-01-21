"""
CRUD operations for Customer entity
Demonstrates basic database operations: CREATE, READ, UPDATE, DELETE
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from app.models.models import Customer
from app.schemas.schemas import CustomerCreate, CustomerUpdate


def get_customer(db: Session, customer_id: int) -> Optional[Customer]:
    """
    Get a single customer by ID
    SQL equivalent: SELECT * FROM customers WHERE id = customer_id;
    """
    return db.query(Customer).filter(Customer.id == customer_id).first()


def get_customer_by_email(db: Session, email: str) -> Optional[Customer]:
    """
    Get a customer by email address
    SQL equivalent: SELECT * FROM customers WHERE email = email;
    """
    return db.query(Customer).filter(Customer.email == email).first()


def get_customers(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    search: Optional[str] = None
) -> List[Customer]:
    """
    Get a list of customers with pagination and optional search
    SQL equivalent: 
    SELECT * FROM customers 
    WHERE name LIKE '%search%' OR email LIKE '%search%'
    LIMIT limit OFFSET skip;
    """
    query = db.query(Customer)
    
    if search:
        query = query.filter(
            or_(
                Customer.name.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%")
            )
        )
    
    return query.offset(skip).limit(limit).all()


def create_customer(db: Session, customer: CustomerCreate) -> Customer:
    """
    Create a new customer
    SQL equivalent: 
    INSERT INTO customers (name, email, phone, address) 
    VALUES (name, email, phone, address);
    """
    db_customer = Customer(**customer.model_dump())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def update_customer(
    db: Session, 
    customer_id: int, 
    customer: CustomerUpdate
) -> Optional[Customer]:
    """
    Update an existing customer
    SQL equivalent: 
    UPDATE customers 
    SET name=name, email=email, phone=phone, address=address 
    WHERE id=customer_id;
    """
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return None
    
    # Update only provided fields
    update_data = customer.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_customer, field, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer


def delete_customer(db: Session, customer_id: int) -> bool:
    """
    Delete a customer
    SQL equivalent: DELETE FROM customers WHERE id = customer_id;
    """
    db_customer = get_customer(db, customer_id)
    if not db_customer:
        return False
    
    db.delete(db_customer)
    db.commit()
    return True
