"""
CRUD operations for Order entity
Demonstrates complex queries with JOINs and relationships
"""
from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from app.models.models import Order, OrderItem, Product
from app.schemas.schemas import OrderCreate


def get_order(db: Session, order_id: int) -> Optional[Order]:
    """
    Get a single order by ID with related items
    SQL equivalent:
    SELECT o.*, oi.*, p.* FROM orders o
    LEFT JOIN order_items oi ON o.id = oi.order_id
    LEFT JOIN products p ON oi.product_id = p.id
    WHERE o.id = order_id;
    """
    return db.query(Order)\
        .options(joinedload(Order.order_items))\
        .filter(Order.id == order_id)\
        .first()


def get_orders(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    customer_id: Optional[int] = None,
    status: Optional[str] = None
) -> List[Order]:
    """
    Get a list of orders with filtering
    SQL equivalent:
    SELECT * FROM orders
    WHERE customer_id = customer_id AND status = status
    LIMIT limit OFFSET skip;
    """
    query = db.query(Order)
    
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    
    if status:
        query = query.filter(Order.status == status)
    
    return query.offset(skip).limit(limit).all()


def get_customer_orders(db: Session, customer_id: int) -> List[Order]:
    """
    Get all orders for a specific customer
    SQL equivalent:
    SELECT o.*, c.name FROM orders o
    JOIN customers c ON o.customer_id = c.id
    WHERE o.customer_id = customer_id;
    """
    return db.query(Order)\
        .filter(Order.customer_id == customer_id)\
        .all()


def create_order(db: Session, order: OrderCreate) -> Order:
    """
    Create a new order with order items
    Demonstrates transaction management and multiple INSERT operations
    
    SQL equivalent:
    BEGIN;
    INSERT INTO orders (customer_id, total_amount, status)
    VALUES (customer_id, 0, 'pending');
    
    INSERT INTO order_items (order_id, product_id, quantity, price_at_time)
    VALUES (order_id, product_id, quantity, price);
    
    UPDATE orders SET total_amount = total WHERE id = order_id;
    COMMIT;
    """
    # Calculate total and create order
    total_amount = 0.0
    
    # Create order
    db_order = Order(
        customer_id=order.customer_id,
        status="pending"
    )
    db.add(db_order)
    db.flush()  # Get the order ID without committing
    
    # Create order items
    for item in order.items:
        # Get product to get current price
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            db.rollback()
            raise ValueError(f"Product with id {item.product_id} not found")
        
        if product.stock < item.quantity:
            db.rollback()
            raise ValueError(f"Insufficient stock for product {product.name}")
        
        # Create order item
        db_order_item = OrderItem(
            order_id=db_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_time=product.price
        )
        db.add(db_order_item)
        
        # Update product stock
        product.stock -= item.quantity
        
        # Add to total
        total_amount += product.price * item.quantity
    
    # Update order total
    db_order.total_amount = total_amount
    
    db.commit()
    db.refresh(db_order)
    return db_order


def update_order_status(db: Session, order_id: int, status: str) -> Optional[Order]:
    """
    Update order status
    SQL equivalent:
    UPDATE orders SET status = status WHERE id = order_id;
    """
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    
    db_order.status = status
    db.commit()
    db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int) -> bool:
    """
    Delete an order (will cascade delete order items)
    SQL equivalent:
    DELETE FROM orders WHERE id = order_id;
    """
    db_order = get_order(db, order_id)
    if not db_order:
        return False
    
    db.delete(db_order)
    db.commit()
    return True
