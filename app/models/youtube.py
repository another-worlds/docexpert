"""
YouTube transcript model for storing video transcripts and metadata.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import hashlib
import re
from urllib.parse import urlparse, parse_qs


@dataclass
class YouTubeTranscript:
    """Model for YouTube video transcripts"""
    user_id: str
    video_id: str
    video_url: str
    title: str
    description: str
    duration: Optional[float]
    language: str
    upload_time: datetime
    transcript_chunks: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'YouTubeTranscript':
        """Create a YouTubeTranscript instance from a dictionary"""
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert YouTubeTranscript instance to dictionary"""
        return {
            "user_id": self.user_id,
            "video_id": self.video_id,
            "video_url": self.video_url,
            "title": self.title,
            "description": self.description,
            "duration": self.duration,
            "language": self.language,
            "upload_time": self.upload_time,
            "transcript_chunks": self.transcript_chunks,
            "metadata": self.metadata
        }
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        # Handle various YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Try parsing as query parameter
        try:
            parsed = urlparse(url)
            if 'v' in parse_qs(parsed.query):
                return parse_qs(parsed.query)['v'][0]
        except:
            pass
        
        return None
    
    @staticmethod
    def is_valid_youtube_url(url: str) -> bool:
        """Check if URL is a valid YouTube URL"""
        youtube_domains = ['youtube.com', 'youtu.be', 'm.youtube.com', 'www.youtube.com']
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower() in youtube_domains
        except:
            return False
    
    @classmethod
    def create(cls, user_id: str, video_url: str, title: str = "", description: str = "", 
               duration: Optional[float] = None, language: str = "en") -> 'YouTubeTranscript':
        """Create a new YouTubeTranscript instance"""
        video_id = cls.extract_video_id(video_url)
        if not video_id:
            raise ValueError(f"Invalid YouTube URL: {video_url}")
        
        return cls(
            user_id=user_id,
            video_id=video_id,
            video_url=video_url,
            title=title,
            description=description,
            duration=duration,
            language=language,
            upload_time=datetime.utcnow(),
            transcript_chunks=[],
            metadata={
                "source": "youtube-transcript-api",
                "processed_at": datetime.utcnow().isoformat()
            }
        )


@dataclass 
class TranscriptChunk:
    """Individual transcript chunk with timing and embedding"""
    text: str
    start_time: float
    duration: float
    embedding: Optional[List[float]] = None
    chunk_index: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage"""
        return {
            "text": self.text,
            "start_time": self.start_time,
            "duration": self.duration,
            "embedding": self.embedding,
            "chunk_index": self.chunk_index
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TranscriptChunk':
        """Create from dictionary"""
        return cls(
            text=data["text"],
            start_time=data["start_time"],
            duration=data["duration"],
            embedding=data.get("embedding"),
            chunk_index=data.get("chunk_index", 0)
        )
