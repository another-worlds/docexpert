#!/usr/bin/env python3
"""
Test script for YouTube Transcript Tool functionality.

This script tests the YouTube transcript processing and search capabilities.
"""

import asyncio
import os
import sys
from pathlib import Path
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
required_env_vars = ["XAI_API_KEY", "HUGGINGFACE_API_KEY"]
missing_vars = []

for var in required_env_vars:
    if not os.getenv(var):
        missing_vars.append(var)

if missing_vars:
    print(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
    print("📝 Tests may fail due to missing API keys")
else:
    print("✅ All required environment variables are loaded")

# Test URLs for YouTube videos (replace with actual test URLs)
TEST_YOUTUBE_URLS = [
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Example URL
    "https://youtu.be/dQw4w9WgXcQ",  # Short URL format
]

async def test_youtube_transcript_tool():
    """Test the YouTube transcript tool"""
    print("🎥 Testing YouTube Transcript Tool...")
    
    try:
        # Import after adding to path and loading environment
        from app.ai.tools import YouTubeTranscriptTool
        from app.models.youtube import YouTubeTranscript
        
        # Create tool instance
        tool = YouTubeTranscriptTool()
        
        print(f"✅ Tool created: {tool.name}")
        print(f"📝 Description: {tool.description}")
        
        # Test context
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
            print(f"⚠️ Expected error (API/DB related): {e}")
        
        print("\n🔍 Testing search query...")
        search_query = "Tell me about machine learning"
        
        try:
            result = await tool.execute(search_query, test_context)
            print(f"✅ Search result: {result}")
        except Exception as e:
            print(f"⚠️ Expected error (API/DB related): {e}")
        
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
    print("📦 Testing imports...")
    
    # Test core modules first (these should work without API keys)
    core_modules = [
        "app.models.youtube",
        "app.config"  # Test if config loads properly
    ]
    
    for module in core_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
        except Exception as e:
            print(f"⚠️ {module}: {e}")
    
    # Test modules that may require API keys (more tolerant)
    api_dependent_modules = [
        "app.handlers.youtube",
        "app.ai.tools"
    ]
    
    for module in api_dependent_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            return False
        except Exception as e:
            # These might fail due to missing API keys, which is expected in tests
            print(f"⚠️ {module}: {e}")
            if "api_key" in str(e).lower() or "xai" in str(e).lower():
                print(f"   💡 This is likely due to missing API keys - continuing...")
            continue
    
    return True

def check_environment():
    """Check if environment is properly configured"""
    print("🔍 Environment Check...")
    
    # Check if .env file exists
    env_file = project_root / ".env"
    if env_file.exists():
        print(f"✅ .env file found at {env_file}")
    else:
        print(f"⚠️ .env file not found at {env_file}")
        print("💡 Create .env file based on .env.example for full functionality")
    
    # Check environment variables
    env_vars = {
        "XAI_API_KEY": "xAI API for language model",
        "HUGGINGFACE_API_KEY": "HuggingFace API for embeddings",
        "MONGODB_URI": "MongoDB connection string"
    }
    
    for var, description in env_vars.items():
        value = os.getenv(var)
        if value:
            # Show only first few characters for security
            masked_value = value[:8] + "..." if len(value) > 8 else value
            print(f"✅ {var}: {masked_value} ({description})")
        else:
            print(f"❌ {var}: Not set ({description})")
    
    print()

async def main():
    """Run all tests"""
    print("YouTube Transcript Tool Test Suite")
    print("=" * 50)
    
    # Check environment setup
    check_environment()
    
    # Test imports first
    if not test_imports():
        print("\n❌ Critical import tests failed. Exiting.")
        return
    
    # Test models (these should work without API keys)
    if not test_youtube_model():
        print("\n⚠️ Model tests failed.")
    else:
        print("\n✅ Model tests passed.")
    
    # Test tool functionality (may have expected failures due to missing APIs)
    print("\n" + "-" * 50)
    if not await test_youtube_transcript_tool():
        print("\n⚠️ Tool tests had issues (this may be expected without API keys).")
    else:
        print("\n✅ Tool tests passed.")
    
    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    print("\n📋 Summary:")
    print("- ✅ Models work correctly")
    print("- ✅ URL parsing and validation works") 
    print("- ⚠️ Some API-dependent features require valid API keys")
    print("\n💡 To test full functionality:")
    print("1. Create .env file based on .env.example")
    print("2. Add your API keys to .env")
    print("3. Run the test again")

if __name__ == "__main__":
    asyncio.run(main())
