#!/usr/bin/env python3
"""
Detailed YouTube Transcript API Error Diagnosis

This script analyzes the specific errors happening with the YouTube Transcript API
and provides detailed diagnostic information.
"""

import sys
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def analyze_youtube_transcript_errors():
    """Analyze and verbalize the YouTube transcript API errors"""
    
    print("🔍 YouTube Transcript API Error Analysis")
    print("=" * 50)
    
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
        print("✅ YouTube Transcript API imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return
    
    # Test video IDs that commonly have transcripts
    test_videos = [
        "M7lc1UVf-VE",  # TED talk
        "jNQXAC9IVRw",  # Tech video  
        "dQw4w9WgXcQ",  # Rick Roll
        "9bZkp7q19f0",  # Popular video
        "LXb3EKWsInQ"   # Another test video
    ]
    
    for video_id in test_videos:
        print(f"\n📺 Analyzing video: {video_id}")
        print(f"🔗 URL: https://www.youtube.com/watch?v={video_id}")
        
        try:
            # Step 1: List available transcripts
            print("   Step 1: Listing available transcripts...")
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            print("   ✅ Successfully listed transcripts")
            
            # Step 2: Check what transcripts are available
            available_transcripts = []
            manual_transcripts = []
            generated_transcripts = []
            
            for transcript in transcript_list:
                lang_code = transcript.language_code
                available_transcripts.append(lang_code)
                
                if transcript.is_generated:
                    generated_transcripts.append(lang_code)
                else:
                    manual_transcripts.append(lang_code)
            
            print(f"   📋 Available languages: {available_transcripts}")
            print(f"   ✍️  Manual transcripts: {manual_transcripts}")
            print(f"   🤖 Generated transcripts: {generated_transcripts}")
            
            # Step 3: Try to get English transcript first
            transcript = None
            for lang in ['en', 'en-US', 'en-GB']:
                try:
                    transcript = transcript_list.find_transcript([lang])
                    print(f"   ✅ Found {lang} transcript")
                    break
                except Exception as e:
                    print(f"   ⚠️ No {lang} transcript: {e}")
            
            # Step 4: If no English, try any available
            if not transcript and available_transcripts:
                try:
                    transcript = transcript_list.find_transcript([available_transcripts[0]])
                    print(f"   ✅ Using {available_transcripts[0]} transcript")
                except Exception as e:
                    print(f"   ❌ Failed to get {available_transcripts[0]} transcript: {e}")
            
            # Step 5: Try to fetch the actual transcript
            if transcript:
                print("   Step 5: Fetching transcript data...")
                try:
                    transcript_data = transcript.fetch()
                    print(f"   ✅ Successfully fetched {len(transcript_data)} transcript entries")
                    
                    # Show sample data
                    if transcript_data:
                        sample = transcript_data[0]
                        print(f"   📝 Sample entry: {sample}")
                        
                        # Check the structure
                        print(f"   🔍 Entry keys: {list(sample.keys())}")
                        
                except Exception as e:
                    print(f"   ❌ Failed to fetch transcript data: {e}")
                    print(f"   🔍 Error type: {type(e).__name__}")
                    print(f"   📝 Full error: {repr(e)}")
                    
                    # Try to get more details about the error
                    if hasattr(e, 'response'):
                        print(f"   🌐 HTTP Response: {e.response}")
                    if hasattr(e, 'status_code'):
                        print(f"   📊 Status Code: {e.status_code}")
            else:
                print("   ❌ No transcript object obtained")
                
        except TranscriptsDisabled:
            print("   ❌ Transcripts are disabled for this video")
        except NoTranscriptFound:
            print("   ❌ No transcripts found for this video")
        except VideoUnavailable:
            print("   ❌ Video is unavailable")
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            print(f"   🔍 Error type: {type(e).__name__}")
            print(f"   📝 Full error details:")
            
            # Print full traceback for debugging
            traceback.print_exc()
            
            # Try to analyze the specific error
            error_str = str(e).lower()
            if "no element found" in error_str:
                print("   🔍 Analysis: XML parsing error - likely malformed response")
                print("   💡 Possible causes:")
                print("      - YouTube changed their API response format")
                print("      - Network interference or proxy issues")
                print("      - Rate limiting or blocking")
                print("      - Video has special characters or encoding issues")
            elif "403" in error_str:
                print("   🔍 Analysis: Access forbidden")
                print("   💡 Possible causes:")
                print("      - IP blocked or rate limited")
                print("      - Geographic restrictions")
                print("      - Video privacy settings")
            elif "404" in error_str:
                print("   🔍 Analysis: Video not found")
                print("   💡 Video may have been deleted or made private")
            
        print("   " + "-" * 40)
    
    print("\n🔍 Error Pattern Analysis:")
    print("The 'no element found: line 1, column 0' error indicates:")
    print("1. 📡 API is receiving empty or malformed XML response")
    print("2. 🚫 Possible rate limiting or IP blocking by YouTube")
    print("3. 🔄 API format changes on YouTube's side")
    print("4. 🌐 Network issues or proxy interference")
    
    print("\n💡 Recommended Solutions:")
    print("1. 🔄 Add retry logic with exponential backoff")
    print("2. 🕐 Add delays between requests")
    print("3. 🔀 Implement user-agent rotation")
    print("4. 📋 Add better error handling for specific error types")
    print("5. 🎯 Use alternative transcript sources when available")
    print("6. 🔍 Add detailed request/response logging")

def test_alternative_approach():
    """Test alternative approaches for getting transcripts"""
    
    print("\n🔬 Testing Alternative Approaches")
    print("=" * 40)
    
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        import time
        import random
        
        # Test with more realistic user agent and delays
        print("Testing with delays and error handling...")
        
        video_id = "dQw4w9WgXcQ"
        
        # Add a small delay to avoid rate limiting
        time.sleep(random.uniform(1, 3))
        
        try:
            # Try with different approach - get transcript directly
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            print(f"✅ Direct method worked! Got {len(transcript)} entries")
            return True
        except Exception as e:
            print(f"❌ Direct method failed: {e}")
        
        try:
            # Try with language specification
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
            print(f"✅ Language-specific method worked! Got {len(transcript)} entries")
            return True
        except Exception as e:
            print(f"❌ Language-specific method failed: {e}")
        
        try:
            # Try with multiple language options
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US', 'auto'])
            print(f"✅ Multi-language method worked! Got {len(transcript)} entries")
            return True
        except Exception as e:
            print(f"❌ Multi-language method failed: {e}")
        
    except Exception as e:
        print(f"❌ Alternative testing failed: {e}")
        
    return False

if __name__ == "__main__":
    analyze_youtube_transcript_errors()
    test_alternative_approach()
    
    print("\n📋 Summary:")
    print("The main issue appears to be XML parsing failures, suggesting:")
    print("1. YouTube API responses are malformed or empty")
    print("2. Possible rate limiting or blocking")
    print("3. Need for more robust error handling")
    print("4. Consider implementing fallback mechanisms")
