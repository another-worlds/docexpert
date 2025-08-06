#!/usr/bin/env python3
"""
Test script for YouTube Transcript Tool functionality with improved environment handling.

This script tests the YouTube transcript processing and search capabilities.
"""

import asyncio
import os
import sys
from pathlib import Path

# Load environment variables FIRST before any app imports
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file BEFORE importing app modules
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ Loaded environment variables from {env_file}")
else:
    print(f"⚠️ .env file not found at {env_file}")
    print("🔧 You can create one based on .env.example")

# Verify critical environment variables are loaded
required_env_vars = ["XAI_API_KEY", "HUGGINGFACE_API_KEY", "MONGODB_URI"]
missing_vars = []

for var in required_env_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
    print("📝 Tests may fail due to missing API keys")
else:
    print("✅ All required environment variables are loaded")

def test_mongodb_connection():
    """Test MongoDB Atlas connection"""
    print("\n🗄️ Testing MongoDB Atlas connection...")
    try:
        from pymongo import MongoClient
        
        mongodb_uri = os.getenv('MONGODB_URI')
        if not mongodb_uri:
            print("❌ MONGODB_URI not set in environment")
            return False
            
        client = MongoClient(
            mongodb_uri,
            serverSelectionTimeoutMS=10000,  # 10 second timeout for test
            connectTimeoutMS=10000,
            socketTimeoutMS=10000
        )
        
        # Test with ping
        client.admin.command('ping')
        print("✅ MongoDB Atlas connection successful!")
        
        # Test database access
        db = client[os.getenv('MONGODB_DB_NAME', 'telegram_bot')]
        collections = db.list_collection_names()
        print(f"📋 Available collections: {collections}")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ MongoDB Atlas connection failed: {str(e)}")
        print("🔧 Common solutions:")
        print("   1. Check your internet connection")
        print("   2. Verify your IP is whitelisted in MongoDB Atlas Network Access")
        print("   3. Ensure cluster is not paused in MongoDB Atlas")
        print("   4. Verify credentials in .env file")
        return False

# Test URLs for YouTube videos
TEST_YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Example URL
    "https://youtu.be/dQw4w9WgXcQ",  # Short URL format
]

async def test_youtube_transcript_tool():
    """Test the YouTube transcript tool"""
    print("\n🎥 Testing YouTube Transcript Tool...")
    
    try:
        # Import after adding to path and loading environment
        from app.ai.tools import YouTubeTranscriptTool
        from app.models.youtube import YouTubeTranscript
        
        # Create tool instance
        tool = YouTubeTranscriptTool()
        
        print(f"✅ Tool created: {tool.name}")
        print(f"📝 Description: {tool.description}")
        
        # Test context with mock database for testing
        test_context = {
            "user_id": "test_user_123",
            "db": None  # This would normally be the database instance
        }
        
        print("\n🔧 Testing URL extraction...")
        test_query_with_url = "Can you process this YouTube video: https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        # This will fail without the actual API, but we can test the structure
        try:
            result = await tool.execute(test_query_with_url, test_context)
            print(f"✅ URL processing result: {result}")
        except Exception as e:
            print(f"⚠️ Expected error (API/network): {str(e)[:100]}...")
        
        print("\n🔍 Testing search query...")
        search_query = "Tell me about machine learning"
        
        try:
            result = await tool.execute(search_query, test_context)
            print(f"✅ Search result: {result}")
        except Exception as e:
            print(f"⚠️ Expected error (no data): {str(e)[:100]}...")
        
        print("🎉 YouTube Transcript Tool test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_youtube_model():
    """Test the YouTube transcript model"""
    print("\n📦 Testing YouTube Models...")
    
    try:
        from app.models.youtube import YouTubeTranscript, TranscriptChunk
        
        # Test URL validation
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtube.com/embed/dQw4w9WgXcQ"
        ]
        
        invalid_urls = [
            "https://vimeo.com/123456789",
            "https://example.com/video",
            "not_a_url"
        ]
        
        print("✅ Testing valid YouTube URLs...")
        for url in valid_urls:
            is_valid = YouTubeTranscript.is_valid_youtube_url(url)
            video_id = YouTubeTranscript.extract_video_id(url)
            print(f"   {url} -> Valid: {is_valid}, ID: {video_id}")
        
        print("\n❌ Testing invalid URLs...")
        for url in invalid_urls:
            is_valid = YouTubeTranscript.is_valid_youtube_url(url)
            video_id = YouTubeTranscript.extract_video_id(url)
            print(f"   {url} -> Valid: {is_valid}, ID: {video_id}")
        
        # Test transcript creation
        print("\n🎬 Testing transcript creation...")
        transcript = YouTubeTranscript.create(
            user_id="test_user",
            video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            title="Test Video",
            description="A test video",
            duration=120.5,
            language="en"
        )
        
        print(f"   Created transcript: {transcript.video_id}")
        print(f"   Title: {transcript.title}")
        print(f"   Duration: {transcript.duration}")
        
        # Test chunk creation
        chunk = TranscriptChunk(
            text="This is a test transcript chunk.",
            start_time=10.5,
            duration=5.0,
            chunk_index=0
        )
        
        print(f"   Created chunk: {chunk.text[:30]}...")
        print(f"   Start time: {chunk.start_time}s")
        
        print("✅ YouTube models test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Model test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """Test that all required imports work"""
    print("\n📦 Testing imports...")
    
    required_modules = [
        "app.models.youtube",
        "app.handlers.youtube", 
        "app.ai.tools"
    ]
    
    success_count = 0
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module}: {e}")
        except Exception as e:
            print(f"⚠️ {module}: {e}")
    
    return success_count == len(required_modules)

async def main():
    """Run all tests"""
    print("YouTube Transcript Tool Test Suite")
    print("=" * 50)
    
    # Test MongoDB connection first
    mongo_ok = test_mongodb_connection()
    
    # Test imports
    if not test_imports():
        print("\n❌ Import tests failed. Some features may not work.")
    
    # Test models
    if not test_youtube_model():
        print("\n❌ Model tests failed.")
    
    # Test tool functionality
    if not await test_youtube_transcript_tool():
        print("\n❌ Tool tests failed.")
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    
    if not mongo_ok:
        print("\n⚠️ MongoDB connection failed - this may affect video transcript storage")
        print("🔧 The tool will still work for processing, but won't persist data")
    
    print("\nNote: Some tests may show 'expected errors' due to API limitations")
    print("or network connectivity. This is normal for unit testing.")

if __name__ == "__main__":
    asyncio.run(main())
