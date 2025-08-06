#!/usr/bin/env python3
"""
MongoDB Atlas Connection Test Utility

This script tests connectivity to MongoDB Atlas and validates the database configuration.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    load_dotenv(env_file)

def test_mongodb_atlas_connection():
    """Test MongoDB Atlas connection and basic operations"""
    
    print("MongoDB Atlas Connection Test")
    print("=" * 40)
    
    # Check environment variables
    mongodb_uri = os.getenv('MONGODB_URI')
    mongodb_db_name = os.getenv('MONGODB_DB_NAME', 'telegram_bot')
    
    if not mongodb_uri:
        print("❌ MONGODB_URI environment variable not set")
        print("💡 Please ensure your .env file contains:")
        print("   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/")
        return False
    
    # Validate URI format
    if not mongodb_uri.startswith(('mongodb://', 'mongodb+srv://')):
        print("❌ Invalid MongoDB URI format")
        print(f"   Current: {mongodb_uri[:50]}...")
        return False
    
    print(f"✅ MongoDB URI format looks correct")
    print(f"📋 Database name: {mongodb_db_name}")
    
    try:
        from pymongo import MongoClient
        from pymongo.errors import ConnectionFailure, OperationFailure
        
        print("\n🔌 Testing connection...")
        
        # Create client with proper timeout settings
        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=30000,  # 30 seconds
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            maxPoolSize=10,
            retryWrites=True
        )
        
        # Test connection with ping
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        
        # Test database access
        db = client[mongodb_db_name]
        
        # List collections
        collections = db.list_collection_names()
        print(f"📋 Available collections: {collections}")
        
        # Test write operation (insert a test document)
        test_collection = db.connection_test
        test_doc = {"test": True, "timestamp": "connection_test"}
        
        # Insert test document
        result = test_collection.insert_one(test_doc)
        print(f"✅ Test write successful, document ID: {result.inserted_id}")
        
        # Read back the test document
        found_doc = test_collection.find_one({"_id": result.inserted_id})
        if found_doc:
            print("✅ Test read successful")
        
        # Clean up test document
        test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Test cleanup successful")
        
        # Get database stats
        stats = db.command("dbstats")
        print(f"📊 Database size: {stats.get('storageSize', 0)} bytes")
        print(f"📊 Collections count: {stats.get('collections', 0)}")
        
        client.close()
        
        print("\n🎉 All MongoDB Atlas tests passed!")
        return True
        
    except ConnectionFailure as e:
        print(f"❌ Connection failed: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("   1. Check your internet connection")
        print("   2. Verify your IP is whitelisted in MongoDB Atlas")
        print("   3. Ensure cluster is not paused")
        print("   4. Verify username/password in connection string")
        return False
        
    except OperationFailure as e:
        print(f"❌ Authentication/authorization failed: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("   1. Verify username and password")
        print("   2. Check database user permissions")
        print("   3. Ensure database user has readWrite role")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_mongodb_atlas_info():
    """Display MongoDB Atlas configuration information"""
    
    print("\n📋 MongoDB Atlas Configuration")
    print("-" * 40)
    
    mongodb_uri = os.getenv('MONGODB_URI', 'Not set')
    mongodb_db_name = os.getenv('MONGODB_DB_NAME', 'telegram_bot')
    
    # Mask sensitive information in URI
    if mongodb_uri != 'Not set' and mongodb_uri.startswith(('mongodb://', 'mongodb+srv://')):
        # Hide password in display
        import re
        masked_uri = re.sub(r'://([^:]+):([^@]+)@', r'://\1:****@', mongodb_uri)
        print(f"🔗 Connection URI: {masked_uri}")
    else:
        print(f"🔗 Connection URI: {mongodb_uri}")
    
    print(f"🗄️  Database name: {mongodb_db_name}")
    
    if mongodb_uri == 'Not set':
        print("\n⚠️  MongoDB Atlas not configured!")
        print("💡 To configure MongoDB Atlas:")
        print("   1. Create account at https://cloud.mongodb.com")
        print("   2. Create a cluster")
        print("   3. Get connection string")
        print("   4. Add MONGODB_URI to your .env file")

if __name__ == "__main__":
    show_mongodb_atlas_info()
    success = test_mongodb_atlas_connection()
    
    if success:
        print("\n✅ MongoDB Atlas is properly configured and accessible!")
        sys.exit(0)
    else:
        print("\n❌ MongoDB Atlas configuration needs attention")
        sys.exit(1)
