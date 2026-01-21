"""
Database Module
===============

This module handles all database operations for the OAuth2 tutorial.
Uses SQLite for simplicity - perfect for learning and small projects.

In production, you might want to use:
- PostgreSQL (recommended for production)
- MySQL
- MongoDB (for NoSQL)

For this tutorial, SQLite is ideal because:
- No installation required
- Single file database
- Perfect for learning
- Easy to backup and share
"""

import sqlite3
import os
from typing import Optional, Dict
from contextlib import contextmanager
from passlib.context import CryptContext

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Database:
    """
    Database class for managing user operations.
    
    This class uses SQLite and provides methods for:
    - Creating tables
    - Adding users
    - Retrieving users
    - Verifying credentials
    """
    
    def __init__(self, db_path: str = "./users.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._create_tables()
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        
        This ensures connections are properly closed even if errors occur.
        
        Usage:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users")
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _create_tables(self):
        """
        Create the users table if it doesn't exist.
        
        Table structure:
        - id: Primary key (auto-increment)
        - username: Unique username
        - full_name: User's full name
        - email: User's email address
        - hashed_password: Bcrypt hashed password
        - disabled: Whether the account is disabled
        - created_at: Timestamp when user was created
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    hashed_password TEXT NOT NULL,
                    disabled BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ Database table 'users' ready")
    
    def create_user(
        self,
        username: str,
        full_name: str,
        email: str,
        password: str,
        disabled: bool = False
    ) -> bool:
        """
        Create a new user in the database.
        
        Args:
            username: Unique username
            full_name: User's full name
            email: User's email
            password: Plain text password (will be hashed)
            disabled: Whether account is disabled
        
        Returns:
            True if user created successfully, False if username exists
        
        Example:
            >>> db = Database()
            >>> db.create_user("john", "John Doe", "john@example.com", "secret")
            True
        """
        try:
            # Hash the password
            hashed_password = pwd_context.hash(password)
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (username, full_name, email, hashed_password, disabled)
                    VALUES (?, ?, ?, ?, ?)
                """, (username, full_name, email, hashed_password, disabled))
                
            print(f"✅ User '{username}' created successfully")
            return True
            
        except sqlite3.IntegrityError:
            print(f"❌ User '{username}' already exists")
            return False
    
    def get_user(self, username: str) -> Optional[Dict]:
        """
        Retrieve a user by username.
        
        Args:
            username: Username to look up
        
        Returns:
            Dictionary with user data if found, None otherwise
        
        Example:
            >>> db = Database()
            >>> user = db.get_user("john")
            >>> print(user["full_name"])
            'John Doe'
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, full_name, email, hashed_password, disabled, created_at
                FROM users
                WHERE username = ?
            """, (username,))
            
            row = cursor.fetchone()
            
            if row:
                # Convert sqlite3.Row to dictionary
                return {
                    "id": row["id"],
                    "username": row["username"],
                    "full_name": row["full_name"],
                    "email": row["email"],
                    "hashed_password": row["hashed_password"],
                    "disabled": bool(row["disabled"]),
                    "created_at": row["created_at"],
                }
            
            return None
    
    def get_all_users(self) -> list:
        """
        Get all users (without passwords).
        
        Returns:
            List of user dictionaries
        
        Example:
            >>> db = Database()
            >>> users = db.get_all_users()
            >>> for user in users:
            ...     print(user["username"])
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, full_name, email, disabled, created_at
                FROM users
            """)
            
            rows = cursor.fetchall()
            
            return [
                {
                    "id": row["id"],
                    "username": row["username"],
                    "full_name": row["full_name"],
                    "email": row["email"],
                    "disabled": bool(row["disabled"]),
                    "created_at": row["created_at"],
                }
                for row in rows
            ]
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Password to verify
            hashed_password: Hashed password from database
        
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username to authenticate
            password: Plain text password
        
        Returns:
            User dictionary if authentication succeeds, None otherwise
        
        Example:
            >>> db = Database()
            >>> user = db.authenticate_user("john", "secret")
            >>> if user:
            ...     print(f"Welcome {user['full_name']}!")
        """
        user = self.get_user(username)
        
        if not user:
            print(f"❌ User '{username}' not found")
            return None
        
        if not self.verify_password(password, user["hashed_password"]):
            print(f"❌ Invalid password for user '{username}'")
            return None
        
        print(f"✅ User '{username}' authenticated successfully")
        return user
    
    def update_user(
        self,
        username: str,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        password: Optional[str] = None
    ) -> bool:
        """
        Update user information.
        
        Args:
            username: Username of user to update
            full_name: New full name (optional)
            email: New email (optional)
            password: New password (optional)
        
        Returns:
            True if update successful, False otherwise
        """
        user = self.get_user(username)
        if not user:
            return False
        
        updates = []
        params = []
        
        if full_name:
            updates.append("full_name = ?")
            params.append(full_name)
        
        if email:
            updates.append("email = ?")
            params.append(email)
        
        if password:
            updates.append("hashed_password = ?")
            params.append(pwd_context.hash(password))
        
        if not updates:
            return True  # Nothing to update
        
        params.append(username)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"""
                UPDATE users
                SET {', '.join(updates)}
                WHERE username = ?
            """, params)
        
        print(f"✅ User '{username}' updated successfully")
        return True
    
    def delete_user(self, username: str) -> bool:
        """
        Delete a user from the database.
        
        Args:
            username: Username to delete
        
        Returns:
            True if deleted, False if user not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            
            if cursor.rowcount > 0:
                print(f"✅ User '{username}' deleted")
                return True
            else:
                print(f"❌ User '{username}' not found")
                return False
    
    def disable_user(self, username: str) -> bool:
        """
        Disable a user account.
        
        Args:
            username: Username to disable
        
        Returns:
            True if successful, False if user not found
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users
                SET disabled = 1
                WHERE username = ?
            """, (username,))
            
            if cursor.rowcount > 0:
                print(f"✅ User '{username}' disabled")
                return True
            else:
                print(f"❌ User '{username}' not found")
                return False


# ==============================================================================
# SINGLETON INSTANCE
# ==============================================================================

# Create a singleton instance that can be imported
# This ensures we only have one database connection throughout the app
_db_instance = None

def get_database(db_path: str = "./users.db") -> Database:
    """
    Get the database instance (singleton pattern).
    
    Args:
        db_path: Path to database file
    
    Returns:
        Database instance
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path)
        
    return _db_instance


# ==============================================================================
# EXAMPLE USAGE
# ==============================================================================

if __name__ == "__main__":
    """
    Demonstration of database operations.
    Run this file directly to see examples.
    """
    print("\n" + "="*60)
    print("Database Module Demo")
    print("="*60 + "\n")
    
    # Create database instance
    db = Database("./demo_users.db")
    
    # Create sample users
    print("\n1. Creating users...")
    db.create_user("john", "John Doe", "john@example.com", "secret")
    db.create_user("jane", "Jane Doe", "jane@example.com", "secret")
    
    # Get a user
    print("\n2. Retrieving user...")
    user = db.get_user("john")
    if user:
        print(f"   Username: {user['username']}")
        print(f"   Full Name: {user['full_name']}")
        print(f"   Email: {user['email']}")
    
    # Authenticate
    print("\n3. Testing authentication...")
    auth_user = db.authenticate_user("john", "secret")
    if auth_user:
        print(f"   ✅ Authentication successful!")
    
    # Wrong password
    auth_user = db.authenticate_user("john", "wrong")
    if not auth_user:
        print(f"   ❌ Authentication failed (as expected)")
    
    # List all users
    print("\n4. All users:")
    users = db.get_all_users()
    for u in users:
        print(f"   - {u['username']}: {u['full_name']}")
    
    print("\n" + "="*60)
    print("Demo complete!")
    print("="*60 + "\n")
    
    # Clean up demo database
    os.remove("./demo_users.db")
    print("Demo database removed.")
