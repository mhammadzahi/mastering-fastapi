"""
SQL Query Examples and Database Setup
This file contains useful SQL queries for learning and testing
"""

-- ==========================================
-- DATABASE SETUP
-- ==========================================

-- Create database
CREATE DATABASE fastapi_db;

-- Connect to database
\c fastapi_db;

-- Create tables (handled by SQLAlchemy, but shown here for reference)

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price FLOAT NOT NULL,
    stock INTEGER DEFAULT 0,
    category VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    total_amount FLOAT DEFAULT 0.0,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES products(id),
    quantity INTEGER NOT NULL DEFAULT 1,
    price_at_time FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_customers_email ON customers(email);
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);


-- ==========================================
-- BASIC QUERIES (SELECT, INSERT, UPDATE, DELETE)
-- ==========================================

-- SELECT: Get all customers
SELECT * FROM customers;

-- SELECT with WHERE: Find customer by email
SELECT * FROM customers WHERE email = 'john@example.com';

-- SELECT with LIKE: Search customers by name
SELECT * FROM customers WHERE name ILIKE '%john%';

-- INSERT: Add new customer
INSERT INTO customers (name, email, phone, address)
VALUES ('John Doe', 'john@example.com', '1234567890', '123 Main St')
RETURNING id;

-- INSERT multiple records
INSERT INTO products (name, description, price, stock, category) VALUES
('Laptop', 'High-performance laptop', 999.99, 10, 'Electronics'),
('Mouse', 'Wireless mouse', 29.99, 50, 'Electronics'),
('Keyboard', 'Mechanical keyboard', 79.99, 30, 'Electronics'),
('Monitor', '27-inch 4K monitor', 399.99, 15, 'Electronics'),
('Desk Chair', 'Ergonomic office chair', 249.99, 20, 'Furniture');

-- UPDATE: Update customer information
UPDATE customers
SET phone = '0987654321', address = '456 Oak Ave', updated_at = CURRENT_TIMESTAMP
WHERE id = 1;

-- UPDATE with calculation: Increase all product prices by 10%
UPDATE products
SET price = price * 1.10, updated_at = CURRENT_TIMESTAMP
WHERE category = 'Electronics';

-- DELETE: Remove customer
DELETE FROM customers WHERE id = 1;

-- DELETE with condition: Remove out-of-stock products
DELETE FROM products WHERE stock = 0;


-- ==========================================
-- JOIN QUERIES
-- ==========================================

-- INNER JOIN: Get orders with customer information
SELECT 
    o.id AS order_id,
    o.total_amount,
    o.status,
    c.name AS customer_name,
    c.email AS customer_email
FROM orders o
INNER JOIN customers c ON o.customer_id = c.id
ORDER BY o.created_at DESC;

-- LEFT JOIN: Get all customers and their orders (including customers without orders)
SELECT 
    c.id,
    c.name,
    c.email,
    COUNT(o.id) AS total_orders,
    COALESCE(SUM(o.total_amount), 0) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name, c.email
ORDER BY total_spent DESC;

-- Multiple JOINs: Get complete order details with products
SELECT 
    o.id AS order_id,
    o.status,
    o.created_at AS order_date,
    c.name AS customer_name,
    c.email AS customer_email,
    p.name AS product_name,
    oi.quantity,
    oi.price_at_time,
    (oi.quantity * oi.price_at_time) AS line_total
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
ORDER BY o.id, p.name;


-- ==========================================
-- AGGREGATION QUERIES
-- ==========================================

-- COUNT: Number of products per category
SELECT 
    category,
    COUNT(*) AS product_count,
    AVG(price) AS avg_price,
    MIN(price) AS min_price,
    MAX(price) AS max_price
FROM products
GROUP BY category
ORDER BY product_count DESC;

-- SUM: Total revenue per customer
SELECT 
    c.name,
    COUNT(o.id) AS total_orders,
    SUM(o.total_amount) AS total_revenue
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE o.status = 'completed'
GROUP BY c.id, c.name
HAVING SUM(o.total_amount) > 100
ORDER BY total_revenue DESC;

-- AVG: Average order value by month
SELECT 
    DATE_TRUNC('month', created_at) AS month,
    COUNT(*) AS order_count,
    AVG(total_amount) AS avg_order_value,
    SUM(total_amount) AS total_revenue
FROM orders
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month DESC;


-- ==========================================
-- SUBQUERIES
-- ==========================================

-- Find customers who have never placed an order
SELECT * FROM customers
WHERE id NOT IN (SELECT DISTINCT customer_id FROM orders);

-- Find products that have never been ordered
SELECT * FROM products
WHERE id NOT IN (SELECT DISTINCT product_id FROM order_items);

-- Find customers with above-average order values
SELECT 
    c.name,
    AVG(o.total_amount) AS avg_order_value
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name
HAVING AVG(o.total_amount) > (SELECT AVG(total_amount) FROM orders);

-- Find top 5 best-selling products
SELECT 
    p.name,
    SUM(oi.quantity) AS total_sold
FROM products p
JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.id, p.name
ORDER BY total_sold DESC
LIMIT 5;


-- ==========================================
-- ADVANCED QUERIES
-- ==========================================

-- CTE (Common Table Expression): Customer lifetime value
WITH customer_stats AS (
    SELECT 
        customer_id,
        COUNT(*) AS order_count,
        SUM(total_amount) AS lifetime_value,
        AVG(total_amount) AS avg_order_value,
        MAX(created_at) AS last_order_date
    FROM orders
    GROUP BY customer_id
)
SELECT 
    c.name,
    c.email,
    cs.order_count,
    cs.lifetime_value,
    cs.avg_order_value,
    cs.last_order_date
FROM customers c
JOIN customer_stats cs ON c.id = cs.customer_id
ORDER BY cs.lifetime_value DESC;

-- Window Function: Rank customers by total spending
SELECT 
    c.name,
    SUM(o.total_amount) AS total_spent,
    RANK() OVER (ORDER BY SUM(o.total_amount) DESC) AS spending_rank
FROM customers c
JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name
ORDER BY spending_rank;

-- Pivot-like query: Sales by category and status
SELECT 
    p.category,
    SUM(CASE WHEN o.status = 'completed' THEN oi.quantity * oi.price_at_time ELSE 0 END) AS completed_sales,
    SUM(CASE WHEN o.status = 'pending' THEN oi.quantity * oi.price_at_time ELSE 0 END) AS pending_sales,
    SUM(CASE WHEN o.status = 'cancelled' THEN oi.quantity * oi.price_at_time ELSE 0 END) AS cancelled_sales
FROM products p
JOIN order_items oi ON p.id = oi.product_id
JOIN orders o ON oi.order_id = o.id
GROUP BY p.category;


-- ==========================================
-- TRANSACTION EXAMPLES
-- ==========================================

-- Begin a transaction to create an order
BEGIN;

-- Insert order
INSERT INTO orders (customer_id, total_amount, status)
VALUES (1, 0, 'pending')
RETURNING id;  -- Get the order_id

-- Insert order items (use the returned order_id)
INSERT INTO order_items (order_id, product_id, quantity, price_at_time)
VALUES (1, 1, 2, 999.99);

-- Update product stock
UPDATE products SET stock = stock - 2 WHERE id = 1;

-- Update order total
UPDATE orders 
SET total_amount = (
    SELECT SUM(quantity * price_at_time) 
    FROM order_items 
    WHERE order_id = 1
)
WHERE id = 1;

-- Commit the transaction
COMMIT;

-- If there's an error, rollback
-- ROLLBACK;


-- ==========================================
-- USEFUL QUERIES FOR REPORTING
-- ==========================================

-- Daily sales report
SELECT 
    DATE(created_at) AS sale_date,
    COUNT(*) AS order_count,
    SUM(total_amount) AS daily_revenue,
    AVG(total_amount) AS avg_order_value
FROM orders
WHERE status = 'completed'
GROUP BY DATE(created_at)
ORDER BY sale_date DESC;

-- Product inventory report
SELECT 
    category,
    name,
    stock,
    price,
    (stock * price) AS inventory_value,
    CASE 
        WHEN stock = 0 THEN 'Out of Stock'
        WHEN stock < 10 THEN 'Low Stock'
        ELSE 'In Stock'
    END AS stock_status
FROM products
ORDER BY category, name;

-- Customer activity report
SELECT 
    c.name,
    c.email,
    COUNT(o.id) AS total_orders,
    MAX(o.created_at) AS last_order_date,
    EXTRACT(DAY FROM CURRENT_TIMESTAMP - MAX(o.created_at)) AS days_since_last_order
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name, c.email
ORDER BY last_order_date DESC NULLS LAST;
