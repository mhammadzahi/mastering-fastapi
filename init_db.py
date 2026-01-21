"""
Initialize Database
===================

This script initializes the SQLite database and creates sample users.

Run this script:
    python init_db.py

This will:
1. Create the database file (users.db)
2. Create the users table
3. Add sample users (john, jane)
"""

import os
from database import Database
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database path from .env or use default
DATABASE_URL = os.getenv("DATABASE_URL", "./users.db")


def init_database():
    """
    Initialize the database with sample users.
    """
    print("\n" + "="*60)
    print("Initializing Database")
    print("="*60 + "\n")
    
    # Create database instance
    print(f"📁 Database path: {DATABASE_URL}")
    db = Database(DATABASE_URL)
    
    # Sample users to create
    sample_users = [
        {
            "username": "john",
            "full_name": "John Doe",
            "email": "john@example.com",
            "password": "secret",
        },
        {
            "username": "jane",
            "full_name": "Jane Doe",
            "email": "jane@example.com",
            "password": "secret",
        },
        {
            "username": "admin",
            "full_name": "Admin User",
            "email": "admin@example.com",
            "password": "admin123",
        },
    ]
    
    print("\n📝 Creating sample users...")
    print("-" * 60)
    
    for user_data in sample_users:
        success = db.create_user(
            username=user_data["username"],
            full_name=user_data["full_name"],
            email=user_data["email"],
            password=user_data["password"],
        )
        
        if success:
            print(f"✅ Created user: {user_data['username']} (password: {user_data['password']})")
        else:
            print(f"⚠️  User '{user_data['username']}' already exists")
    
    print("\n" + "-" * 60)
    print("📊 Current users in database:")
    print("-" * 60)
    
    users = db.get_all_users()
    for user in users:
        status = "🔒 Disabled" if user["disabled"] else "✅ Active"
        print(f"{status} | {user['username']:10} | {user['full_name']:20} | {user['email']}")
    
    print("\n" + "="*60)
    print("✅ Database initialization complete!")
    print("="*60)
    
    print("\n💡 Test Credentials:")
    print("-" * 60)
    for user_data in sample_users:
        print(f"   Username: {user_data['username']:10} Password: {user_data['password']}")
    print("-" * 60)
    
    print("\n🚀 You can now run the application:")
    print("   uvicorn app:app --reload")
    print("\n")


def reset_database():
    """
    Reset the database by deleting the file and recreating it.
    Use with caution!
    """
    if os.path.exists(DATABASE_URL):
        response = input(f"\n⚠️  Delete existing database '{DATABASE_URL}'? (yes/no): ")
        if response.lower() == "yes":
            os.remove(DATABASE_URL)
            print(f"✅ Deleted {DATABASE_URL}")
        else:
            print("❌ Cancelled")
            return False
    
    return True


if __name__ == "__main__":
    import sys
    
    try:
        # Check if user wants to reset database
        if "--reset" in sys.argv:
            if reset_database():
                init_database()
        else:
            # Check if database already exists
            if os.path.exists(DATABASE_URL):
                print(f"\n⚠️  Database '{DATABASE_URL}' already exists.")
                print("   This will add new users if they don't exist.")
                print("   To reset the database, run: python init_db.py --reset\n")
                
                response = input("Continue? (yes/no): ").strip().lower()
                if response != "yes":
                    print("❌ Cancelled")
                    sys.exit(0)
            
            init_database()
    
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
