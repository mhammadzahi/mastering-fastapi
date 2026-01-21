# FastAPI Product & Customer Management API

A comprehensive FastAPI application demonstrating RESTful API development with PostgreSQL, SQLAlchemy, Pydantic validation, and custom middleware.

## 📋 Features

- **RESTful API Endpoints**: Full CRUD operations (GET, POST, PUT, DELETE)
- **PostgreSQL Integration**: Using SQLAlchemy ORM
- **Data Validation**: Pydantic models for request/response validation
- **Custom Middleware**: Logging, CORS, and Authentication placeholder
- **Relationships**: Demonstrates JOIN operations between tables
- **Advanced Filtering**: Search, pagination, and multi-criteria filtering
- **Transaction Management**: Complex operations with rollback support
- **API Documentation**: Auto-generated with Swagger UI and ReDoc

## 🏗️ Project Structure

```
mastering-fastapi/
├── app/
│   ├── __init__.py
│   ├── database.py              # Database configuration
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py            # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── schemas.py           # Pydantic schemas
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── customer.py          # Customer CRUD operations
│   │   ├── product.py           # Product CRUD operations
│   │   └── order.py             # Order CRUD operations
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── customers.py         # Customer endpoints
│   │   ├── products.py          # Product endpoints
│   │   └── orders.py            # Order endpoints
│   └── middleware/
│       ├── __init__.py
│       ├── logging.py           # Logging middleware
│       └── auth.py              # Authentication middleware
├── main.py                      # FastAPI application entry point
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 12+
- Virtual environment (recommended)

### 1. Setup PostgreSQL Database

```sql
-- Connect to PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE fastapi_db;

-- Create user (optional)
CREATE USER fastapi_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fastapi_db TO fastapi_user;
```

### 2. Install Dependencies

```bash
# Activate virtual environment
source env/bin/activate  # On Linux/Mac
# or
env\Scripts\activate     # On Windows

# Install required packages
pip install psycopg2-binary email-validator
```

### 3. Configure Database Connection

Update the database URL in `app/database.py`:

```python
DATABASE_URL = "postgresql://username:password@localhost:5432/fastapi_db"
```

Or create a `.env` file:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/fastapi_db
```

### 4. Run the Application

```bash
# Using Python
python main.py

# Or using Uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📊 Database Schema

### Tables

1. **customers**: Customer information
2. **products**: Product catalog
3. **orders**: Customer orders
4. **order_items**: Order details (many-to-many relationship)

### Relationships

```
customers (1) ──< (N) orders (1) ──< (N) order_items >── (N) products
```

## 🔌 API Endpoints

### Customers

- `GET /api/customers/` - List all customers (with pagination and search)
- `GET /api/customers/{id}` - Get customer by ID
- `POST /api/customers/` - Create new customer
- `PUT /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Delete customer

### Products

- `GET /api/products/` - List all products (with filtering)
- `GET /api/products/{id}` - Get product by ID
- `POST /api/products/` - Create new product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product

### Orders

- `GET /api/orders/` - List all orders (with filtering)
- `GET /api/orders/{id}` - Get order by ID
- `GET /api/orders/customer/{customer_id}` - Get customer's orders
- `POST /api/orders/` - Create new order
- `PUT /api/orders/{id}` - Update order status
- `DELETE /api/orders/{id}` - Delete order

## 📝 SQL Query Examples

### Basic Queries

```sql
-- SELECT: Get all customers
SELECT * FROM customers;

-- SELECT with WHERE: Find customer by email
SELECT * FROM customers WHERE email = 'john@example.com';

-- INSERT: Add new customer
INSERT INTO customers (name, email, phone, address)
VALUES ('John Doe', 'john@example.com', '1234567890', '123 Main St');

-- UPDATE: Update customer information
UPDATE customers
SET phone = '0987654321', address = '456 Oak Ave'
WHERE id = 1;

-- DELETE: Remove customer
DELETE FROM customers WHERE id = 1;
```

### Advanced Queries

```sql
-- JOIN: Get orders with customer information
SELECT o.id, o.total_amount, c.name, c.email
FROM orders o
JOIN customers c ON o.customer_id = c.id;

-- Complex JOIN: Get order details with product information
SELECT 
    o.id AS order_id,
    c.name AS customer_name,
    p.name AS product_name,
    oi.quantity,
    oi.price_at_time,
    (oi.quantity * oi.price_at_time) AS line_total
FROM orders o
JOIN customers c ON o.customer_id = c.id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
ORDER BY o.id;

-- Aggregation: Get total sales per customer
SELECT 
    c.name,
    COUNT(o.id) AS total_orders,
    SUM(o.total_amount) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id
GROUP BY c.id, c.name
ORDER BY total_spent DESC;

-- Subquery: Find products that have never been ordered
SELECT * FROM products
WHERE id NOT IN (
    SELECT DISTINCT product_id FROM order_items
);

-- Filter products by stock and price
SELECT * FROM products
WHERE stock > 0 AND price BETWEEN 10 AND 100
ORDER BY price ASC;
```

## 🧪 Testing the API

### Using cURL

```bash
# Create a customer
curl -X POST "http://localhost:8000/api/customers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "address": "123 Main St"
  }'

# Get all customers
curl "http://localhost:8000/api/customers/"

# Create a product
curl -X POST "http://localhost:8000/api/products/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "stock": 10,
    "category": "Electronics"
  }'

# Create an order
curl -X POST "http://localhost:8000/api/orders/" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": 1,
    "items": [
      {"product_id": 1, "quantity": 2}
    ]
  }'
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Create customer
customer_data = {
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "9876543210"
}
response = requests.post(f"{BASE_URL}/customers/", json=customer_data)
customer = response.json()
print(f"Created customer: {customer}")

# Get all products
response = requests.get(f"{BASE_URL}/products/")
products = response.json()
print(f"Total products: {len(products)}")

# Update product
update_data = {"stock": 15}
response = requests.put(f"{BASE_URL}/products/1", json=update_data)
print(f"Updated product: {response.json()}")
```

## 🔐 Middleware

### Logging Middleware
Logs all incoming requests with:
- HTTP method and path
- Client IP address
- Response status code
- Processing time

### CORS Middleware
Configured to allow:
- All origins (configure for production)
- All HTTP methods
- All headers

### Authentication Middleware (Placeholder)
- Checks for `X-API-Key` header
- Public paths bypass authentication
- Ready for JWT implementation

## 📦 Dependencies

```
fastapi>=0.109.0
uvicorn>=0.27.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
pydantic>=2.12.0
pydantic[email]
python-jose[cryptography]
passlib[bcrypt]
python-multipart
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/fastapi_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 📚 Learning Resources

### SQLAlchemy ORM
- Declarative models with relationships
- Query building and filtering
- Transaction management
- Connection pooling

### Pydantic Validation
- Type validation
- Field constraints (min_length, max_length, gt, ge)
- Email validation
- Custom validators

### FastAPI Features
- Dependency injection
- Path and query parameters
- Request/response models
- Automatic API documentation
- Middleware system

## 🎯 Next Steps

1. **Add Authentication**: Implement JWT token-based authentication
2. **Add Tests**: Write unit and integration tests
3. **Add Migrations**: Use Alembic for database migrations
4. **Add Caching**: Implement Redis for caching
5. **Add Pagination**: Implement cursor-based pagination
6. **Add Rate Limiting**: Implement rate limiting middleware
7. **Add Background Tasks**: Use Celery for async tasks
8. **Deploy**: Deploy to cloud (AWS, Azure, GCP)

## 📄 License

This project is for educational purposes.

## 👤 Author

Created as a learning project for FastAPI and PostgreSQL integration.
