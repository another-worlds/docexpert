#!/usr/bin/env python3
"""
Test YouTube transcript functionality with real videos
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

async def test_youtube_transcript_api():
    """Test the YouTube transcript API directly"""
    print("🎥 Testing YouTube Transcript API...")
    
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        print("✅ YouTube Transcript API imported successfully")
        
        # Test with different videos that are likely to have transcripts
        test_videos = [
            "M7lc1UVf-VE",  # TED talk - usually has good transcripts
            "jNQXAC9IVRw",  # "Me at the zoo" - first YouTube video
            "dQw4w9WgXcQ",  # Rick Roll - popular video
            "9bZkp7q19f0",  # Gangnam Style - popular video
        ]
        
        for video_id in test_videos:
            print(f"\n📺 Testing video: {video_id}")
            
            try:
                # Try to get transcript
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                print(f"✅ Success! Got {len(transcript)} transcript entries")
                print(f"📝 First entry: {transcript[0] if transcript else 'None'}")
                
                # Test the transcript list functionality
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    available_langs = []
                    for t in transcript_list:
                        available_langs.append(t.language_code)
                    print(f"🌐 Available languages: {available_langs}")
                except Exception as e:
                    print(f"⚠️ Could not list transcripts: {e}")
                
                return video_id, transcript  # Return first working video
                
            except Exception as e:
                print(f"❌ Failed for {video_id}: {e}")
                continue
        
        print("❌ No working videos found")
        return None, None
        
    except ImportError:
        print("❌ YouTube Transcript API not installed")
        print("💡 Install with: pip install youtube-transcript-api")
        return None, None

async def test_youtube_handler():
    """Test the YouTube handler with a working video"""
    print("\n🔧 Testing YouTube Handler...")
    
    try:
        from app.handlers.youtube import YouTubeTranscriptHandler
        
        handler = YouTubeTranscriptHandler()
        
        # Test with a video that should have transcripts
        test_video_url = "https://www.youtube.com/watch?v=M7lc1UVf-VE"  # TED talk
        
        print(f"🎯 Testing with: {test_video_url}")
        
        result = await handler.process_youtube_url("test_user", test_video_url)
        
        if "error" in result:
            print(f"❌ Handler error: {result['error']}")
        else:
            print(f"✅ Handler success: {result}")
            
        return result
        
    except Exception as e:
        print(f"❌ Handler test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_youtube_tool():
    """Test the YouTube AI tool"""
    print("\n🤖 Testing YouTube AI Tool...")
    
    try:
        from app.ai.tools import YouTubeTranscriptTool
        
        tool = YouTubeTranscriptTool()
        
        # Test with URL processing
        test_query = "Can you process this video: https://www.youtube.com/watch?v=M7lc1UVf-VE"
        
        # Mock context
        context = {
            "user_id": "test_user",
            "db": None  # Would be database instance in real usage
        }
        
        print(f"🎯 Testing query: {test_query}")
        
        result = await tool.execute(test_query, context)
        
        print(f"🤖 AI Tool result: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ AI Tool test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

async def main():
    """Run all YouTube tests"""
    print("YouTube Transcript Integration Test")
    print("=" * 50)
    
    # Test 1: Direct API test
    working_video, transcript = await test_youtube_transcript_api()
    
    # Test 2: Handler test
    if working_video:
        await test_youtube_handler()
    
    # Test 3: AI Tool test
    await test_youtube_tool()
    
    print("\n" + "=" * 50)
    print("🎉 All YouTube tests completed!")
    
    if working_video:
        print(f"✅ Found working video: {working_video}")
        print("🎯 YouTube transcript integration should work!")
    else:
        print("⚠️ No working videos found - check network connection")

if __name__ == "__main__":
    asyncio.run(main())
