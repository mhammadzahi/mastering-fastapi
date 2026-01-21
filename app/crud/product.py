"""
CRUD operations for Product entity
Demonstrates database operations with filtering and sorting
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from app.models.models import Product
from app.schemas.schemas import ProductCreate, ProductUpdate


def get_product(db: Session, product_id: int) -> Optional[Product]:
    """
    Get a single product by ID
    SQL equivalent: SELECT * FROM products WHERE id = product_id;
    """
    return db.query(Product).filter(Product.id == product_id).first()


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None
) -> List[Product]:
    """
    Get a list of products with advanced filtering
    SQL equivalent:
    SELECT * FROM products
    WHERE category = category
      AND (name LIKE '%search%' OR description LIKE '%search%')
      AND price >= min_price
      AND price <= max_price
      AND stock > 0
    LIMIT limit OFFSET skip;
    """
    query = db.query(Product)
    
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        query = query.filter(
            or_(
                Product.name.ilike(f"%{search}%"),
                Product.description.ilike(f"%{search}%")
            )
        )
    
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    if in_stock:
        query = query.filter(Product.stock > 0)
    
    return query.offset(skip).limit(limit).all()


def create_product(db: Session, product: ProductCreate) -> Product:
    """
    Create a new product
    SQL equivalent:
    INSERT INTO products (name, description, price, stock, category)
    VALUES (name, description, price, stock, category);
    """
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(
    db: Session,
    product_id: int,
    product: ProductUpdate
) -> Optional[Product]:
    """
    Update an existing product
    SQL equivalent:
    UPDATE products
    SET name=name, description=description, price=price, stock=stock, category=category
    WHERE id=product_id;
    """
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    
    # Update only provided fields
    update_data = product.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> bool:
    """
    Delete a product
    SQL equivalent: DELETE FROM products WHERE id = product_id;
    """
    db_product = get_product(db, product_id)
    if not db_product:
        return False
    
    db.delete(db_product)
    db.commit()
    return True


def update_stock(db: Session, product_id: int, quantity_change: int) -> Optional[Product]:
    """
    Update product stock (add or subtract)
    SQL equivalent:
    UPDATE products SET stock = stock + quantity_change WHERE id = product_id;
    """
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    
    db_product.stock += quantity_change
    db.commit()
    db.refresh(db_product)
    return db_product
