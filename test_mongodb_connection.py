#!/usr/bin/env python3
"""
MongoDB Atlas Connection Test

This script tests the connection to MongoDB Atlas using the configured environment variables.
Run this before running the main application to verify connectivity.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment variables from {env_file}")
else:
    print(f"⚠️ .env file not found at {env_file}")

def test_mongodb_connection():
    """Test MongoDB Atlas connection"""
    try:
        from pymongo import MongoClient
        from app.config import MONGODB_URI, MONGODB_DB_NAME
        
        print("🔧 Testing MongoDB Atlas connection...")
        print(f"📍 Database: {MONGODB_DB_NAME}")
        print(f"🌐 URI: {MONGODB_URI[:50]}...")
        
        # Create client with shorter timeout for testing
        client = MongoClient(
            MONGODB_URI,
            serverSelectionTimeoutMS=10000,  # 10 second timeout
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        
        # Test connection
        print("🔄 Attempting to connect...")
        client.admin.command('ping')
        print("✅ MongoDB Atlas connection successful!")
        
        # Test database access
        db = client[MONGODB_DB_NAME]
        collections = db.list_collection_names()
        print(f"📊 Available collections: {collections}")
        
        # Test a simple operation
        test_collection = db['test_connection']
        result = test_collection.insert_one({"test": "connection", "status": "success"})
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Clean up test document
        test_collection.delete_one({"_id": result.inserted_id})
        print("🧹 Test document cleaned up")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check if your IP is whitelisted in MongoDB Atlas Network Access")
        print("2. Verify your MongoDB credentials in .env file")
        print("3. Ensure your internet connection is stable")
        print("4. Check MongoDB Atlas cluster status")
        return False

def verify_environment():
    """Verify required environment variables"""
    print("\n🔍 Verifying environment variables...")
    
    required_vars = [
        "MONGODB_URI",
        "MONGODB_DB_NAME", 
        "XAI_API_KEY",
        "HUGGINGFACE_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "API_KEY" in var or "PASSWORD" in var or "URI" in var:
                masked_value = value[:10] + "..." if len(value) > 10 else "***"
                print(f"  ✅ {var}: {masked_value}")
            else:
                print(f"  ✅ {var}: {value}")
        else:
            missing_vars.append(var)
            print(f"  ❌ {var}: NOT SET")
    
    if missing_vars:
        print(f"\n⚠️ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ All required environment variables are set")
    return True

def main():
    """Main test function"""
    print("MongoDB Atlas Connection Test")
    print("=" * 50)
    
    # Verify environment variables first
    if not verify_environment():
        print("\n❌ Environment verification failed. Please check your .env file.")
        return False
    
    # Test MongoDB connection
    if not test_mongodb_connection():
        print("\n❌ MongoDB connection test failed.")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! Your MongoDB Atlas setup is working correctly.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
