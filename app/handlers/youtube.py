"""
YouTube transcript handler for processing and storing video transcripts.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter
except ImportError:
    YouTubeTranscriptApi = None
    TextFormatter = None

from ..models.youtube import YouTubeTranscript, TranscriptChunk
from ..services.embedding import embedding_service
from ..database.mongodb import db
from ..utils.logging import get_logger
from ..utils.text import normalize_text
from ..config import VECTOR_DIMENSIONS

# Setup logger
youtube_logger = get_logger('youtube_handler')


class YouTubeTranscriptHandler:
    """Handler for YouTube transcript processing and storage"""
    
    def __init__(self):
        self.db = db
        self.embedding_service = embedding_service
        
        # Check if YouTube transcript API is available
        if not YouTubeTranscriptApi:
            youtube_logger.warning("⚠️ YouTube Transcript API not installed. Install with: pip install youtube-transcript-api")
        else:
            youtube_logger.info("✅ YouTube Transcript API initialized")
    
    async def process_youtube_url(self, user_id: str, video_url: str) -> Dict[str, Any]:
        """
        Process a YouTube URL and store the transcript
        
        Args:
            user_id: User identifier
            video_url: YouTube video URL
            
        Returns:
            Dict with processing results
        """
        try:
            if not YouTubeTranscriptApi:
                return {"error": "YouTube Transcript API not available"}
            
            youtube_logger.info(f"🎥 Processing YouTube URL: {video_url}")
            
            # Validate URL and extract video ID
            if not YouTubeTranscript.is_valid_youtube_url(video_url):
                return {"error": "Invalid YouTube URL provided"}
            
            video_id = YouTubeTranscript.extract_video_id(video_url)
            if not video_id:
                return {"error": "Could not extract video ID from URL"}
            
            # Check if transcript already exists
            existing = await self._get_existing_transcript(user_id, video_id)
            if existing:
                youtube_logger.info(f"📋 Transcript already exists for video {video_id}")
                return {
                    "message": "Transcript already processed",
                    "video_id": video_id,
                    "transcript_id": str(existing["_id"])
                }
            
            # Fetch transcript from YouTube
            transcript_data = await self._fetch_transcript(video_id)
            if "error" in transcript_data:
                return transcript_data
            
            # Create transcript model
            transcript = YouTubeTranscript.create(
                user_id=user_id,
                video_url=video_url,
                title=transcript_data.get("title", f"YouTube Video {video_id}"),
                description=transcript_data.get("description", ""),
                duration=transcript_data.get("duration"),
                language=transcript_data.get("language", "en")
            )
            
            # Process and chunk the transcript
            chunks = await self._process_transcript_chunks(
                transcript_data["transcript"], 
                video_id
            )
            
            # Generate embeddings for chunks
            await self._generate_embeddings(chunks)
            
            # Store in database
            transcript.transcript_chunks = [chunk.to_dict() for chunk in chunks]
            result = await self._store_transcript(transcript)
            
            youtube_logger.info(f"✅ Successfully processed transcript for {video_id} with {len(chunks)} chunks")
            
            return {
                "message": "Transcript processed successfully",
                "video_id": video_id,
                "video_url": video_url,
                "title": transcript.title,
                "chunks_count": len(chunks),
                "transcript_id": str(result.inserted_id)
            }
            
        except Exception as e:
            youtube_logger.error(f"❌ Error processing YouTube URL: {str(e)}")
            return {"error": f"Failed to process YouTube URL: {str(e)}"}
    
    async def search_transcripts(self, user_id: str, query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Search user's YouTube transcripts for relevant content
        
        Args:
            user_id: User identifier
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Dict with search results
        """
        try:
            youtube_logger.info(f"🔍 Searching transcripts for user {user_id}: '{query}'")
            
            # Generate query embedding
            query_embedding = await self.embedding_service.embed_query(query)
            
            # Search in MongoDB using vector similarity
            pipeline = [
                {"$match": {"user_id": user_id}},
                {"$unwind": "$transcript_chunks"},
                {"$match": {"transcript_chunks.embedding": {"$exists": True}}},
                {
                    "$addFields": {
                        "similarity": {
                            "$let": {
                                "vars": {
                                    "dot_product": {
                                        "$reduce": {
                                            "input": {"$range": [0, len(query_embedding)]},
                                            "initialValue": 0,
                                            "in": {
                                                "$add": [
                                                    "$$value",
                                                    {
                                                        "$multiply": [
                                                            {"$arrayElemAt": [query_embedding, "$$this"]},
                                                            {"$arrayElemAt": ["$transcript_chunks.embedding", "$$this"]}
                                                        ]
                                                    }
                                                ]
                                            }
                                        }
                                    }
                                },
                                "in": "$$dot_product"
                            }
                        }
                    }
                },
                {"$sort": {"similarity": -1}},
                {"$limit": limit},
                {
                    "$project": {
                        "video_id": 1,
                        "video_url": 1,
                        "title": 1,
                        "chunk_text": "$transcript_chunks.text",
                        "start_time": "$transcript_chunks.start_time",
                        "duration": "$transcript_chunks.duration",
                        "similarity": 1
                    }
                }
            ]
            
            results = list(self.db.db["youtube_transcripts"].aggregate(pipeline))
            
            youtube_logger.info(f"📊 Found {len(results)} relevant transcript chunks")
            
            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "video_id": result["video_id"],
                    "video_url": result["video_url"],
                    "title": result["title"],
                    "text": result["chunk_text"],
                    "timestamp": self._format_timestamp(result["start_time"]),
                    "similarity": result["similarity"],
                    "context": f"From video '{result['title']}' at {self._format_timestamp(result['start_time'])}"
                })
            
            return {
                "results": formatted_results,
                "total_found": len(formatted_results),
                "query": query
            }
            
        except Exception as e:
            youtube_logger.error(f"❌ Error searching transcripts: {str(e)}")
            return {"error": f"Failed to search transcripts: {str(e)}"}
    
    async def _fetch_transcript(self, video_id: str) -> Dict[str, Any]:
        """Fetch transcript from YouTube API with enhanced error handling and rate limiting"""
        if not YouTubeTranscriptApi:
            return {"error": "YouTube Transcript API not available. Install with: pip install youtube-transcript-api"}
        
        # Implement exponential backoff for rate limiting
        max_retries = 3
        base_delay = 5.0  # Start with 5 second delay to be more respectful
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    delay = base_delay * (2 ** (attempt - 1))  # Exponential backoff
                    youtube_logger.info(f"⏳ Rate limit backoff: waiting {delay}s before retry {attempt + 1}")
                    await asyncio.sleep(delay)
                
                youtube_logger.info(f"🎥 Fetching transcript for video: {video_id} (attempt {attempt + 1})")
                
                # Add initial delay to be respectful to YouTube's API
                await asyncio.sleep(2)
                
                # Get available transcripts
                try:
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                except Exception as e:
                    error_msg = str(e)
                    if "429" in error_msg or "Too Many Requests" in error_msg:
                        youtube_logger.warning(f"🚫 Rate limited while listing transcripts: {video_id}")
                        if attempt < max_retries - 1:
                            continue  # Retry with backoff
                        else:
                            return {"error": "YouTube API rate limited. Please try again later."}
                    elif "private" in error_msg.lower():
                        return {"error": "Video is private or restricted"}
                    elif "unavailable" in error_msg.lower() or "disabled" in error_msg.lower():
                        return {"error": "Video is unavailable or has disabled transcripts"}
                    elif "not found" in error_msg.lower():
                        return {"error": "Video not found"}
                    else:
                        return {"error": f"Failed to access video: {error_msg}"}
                
                # Try to get English transcript first, then other languages
                transcript = None
                language_priorities = ['en', 'en-US', 'en-GB', 'auto']
                
                # First try preferred languages
                for lang in language_priorities:
                    try:
                        transcript = transcript_list.find_transcript([lang])
                        youtube_logger.info(f"✅ Found transcript in language: {lang}")
                        break
                    except:
                        continue
                
                # If no preferred language found, get any available transcript
                if not transcript:
                    available_transcripts = []
                    for t in transcript_list:
                        available_transcripts.append(t.language_code)
                    
                    youtube_logger.info(f"📋 Available transcript languages: {available_transcripts}")
                    
                    if available_transcripts:
                        # Get the first available transcript
                        transcript = transcript_list.find_transcript([available_transcripts[0]])
                        youtube_logger.info(f"✅ Using available transcript: {available_transcripts[0]}")
                    else:
                        return {"error": "No transcripts available for this video"}

                if not transcript:
                    return {"error": "No transcript available for this video"}

                # Add another delay before fetching actual transcript data
                await asyncio.sleep(2)

                # Fetch the actual transcript with error handling
                try:
                    transcript_data = transcript.fetch()
                except Exception as e:
                    error_msg = str(e)
                    error_type = type(e).__name__
                    status_code = getattr(e, 'status_code', None)
                    details = f"{error_type}: {error_msg}"
                    if status_code:
                        details += f" (HTTP {status_code})"
                    if "429" in error_msg or "Too Many Requests" in error_msg or (status_code == 429):
                        youtube_logger.warning(f"🚫 Rate limited while fetching transcript: {video_id} | {details}")
                        if attempt < max_retries - 1:
                            continue  # Retry with backoff
                        else:
                            return {"error": f"YouTube API rate limited. Details: {details}"}
                    else:
                        youtube_logger.error(f"❌ Failed to fetch transcript data: {details}")
                        return {"error": f"Failed to fetch transcript: {details}"}
                
                if not transcript_data:
                    return {"error": "Transcript data is empty"}
                
                youtube_logger.info(f"📝 Successfully fetched transcript with {len(transcript_data)} entries in {transcript.language_code}")
                
                # Try to get video metadata (basic info from transcript API)
                video_title = f"YouTube Video {video_id}"
                
                # Some transcripts might have video title in metadata
                try:
                    if hasattr(transcript, 'video_title'):
                        video_title = transcript.video_title
                except:
                    pass
                
                return {
                    "transcript": transcript_data,
                    "language": transcript.language_code,
                    "title": video_title,
                    "description": "",
                    "video_id": video_id
                }
                
            except Exception as e:
                error_msg = str(e)
                error_type = type(e).__name__
                status_code = getattr(e, 'status_code', None)
                details = f"{error_type}: {error_msg}"
                if status_code:
                    details += f" (HTTP {status_code})"
                youtube_logger.error(f"❌ Attempt {attempt + 1} failed: {details}")
                # Check if it's a rate limiting error
                if "429" in error_msg or "Too Many Requests" in error_msg or (status_code == 429):
                    if attempt < max_retries - 1:
                        continue  # Retry with backoff
                    else:
                        return {"error": f"YouTube API rate limited after multiple attempts. Details: {details}"}
                # For other errors on final attempt, return them
                if attempt == max_retries - 1:
                    if "No transcripts were found" in error_msg:
                        return {"error": "No transcripts available for this video"}
                    elif "Could not retrieve a transcript" in error_msg:
                        return {"error": "Transcript could not be retrieved (may be disabled)"}
                    elif "HTTP Error 404" in error_msg:
                        return {"error": "Video not found"}
                    else:
                        return {"error": f"Failed to fetch transcript: {details}"}
        
        # This should never be reached, but just in case
        return {"error": "Failed to fetch transcript after all retry attempts"}
    
    async def _process_transcript_chunks(self, transcript_data: List[Dict], video_id: str) -> List[TranscriptChunk]:
        """Process transcript into chunks suitable for embedding"""
        chunks = []
        
        # Combine transcript entries into larger, more meaningful chunks
        current_text = ""
        start_time = 0
        chunk_duration = 0
        chunk_index = 0
        
        for i, entry in enumerate(transcript_data):
            text = normalize_text(entry.get('text', ''))
            if not text:
                continue
            
            if not current_text:  # Start new chunk
                start_time = entry.get('start', 0)
                current_text = text
                chunk_duration = entry.get('duration', 0)
            else:
                current_text += " " + text
                chunk_duration += entry.get('duration', 0)
            
            # Create chunk when we have enough content or reach the end
            if len(current_text) >= 500 or i == len(transcript_data) - 1:
                if current_text.strip():
                    chunk = TranscriptChunk(
                        text=current_text.strip(),
                        start_time=start_time,
                        duration=chunk_duration,
                        chunk_index=chunk_index
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                
                # Reset for next chunk
                current_text = ""
                chunk_duration = 0
        
        youtube_logger.info(f"📊 Created {len(chunks)} transcript chunks")
        return chunks
    
    async def _generate_embeddings(self, chunks: List[TranscriptChunk]):
        """Generate embeddings for transcript chunks"""
        if not chunks:
            return
        
        texts = [chunk.text for chunk in chunks]
        embeddings = await self.embedding_service.embed_documents(texts)
        
        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding
        
        youtube_logger.info(f"🧠 Generated embeddings for {len(chunks)} chunks")
    
    async def _store_transcript(self, transcript: YouTubeTranscript):
        """Store transcript in MongoDB"""
        # Ensure youtube_transcripts collection exists
        if 'youtube_transcripts' not in self.db.db.list_collection_names():
            self.db.db.create_collection('youtube_transcripts')
            # Create index for user_id and video_id
            self.db.db["youtube_transcripts"].create_index([("user_id", 1), ("video_id", 1)])
            self.db.db["youtube_transcripts"].create_index([("user_id", 1)])
        
        return self.db.db["youtube_transcripts"].insert_one(transcript.to_dict())
    
    async def _get_existing_transcript(self, user_id: str, video_id: str) -> Optional[Dict]:
        """Check if transcript already exists"""
        if 'youtube_transcripts' not in self.db.db.list_collection_names():
            return None
        
        return self.db.db["youtube_transcripts"].find_one({
            "user_id": user_id,
            "video_id": video_id
        })
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds to MM:SS format"""
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"


# Global instance
youtube_handler = YouTubeTranscriptHandler()
