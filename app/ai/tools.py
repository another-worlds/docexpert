"""
AI Tools for the DocExpert system.

This module contains concrete implementations of AI tools that can be used
by various agents in the system.
"""

from typing import Dict, Any, Optional
import asyncio
import re
from .base import AITool
from ..handlers.document import document_handler
from ..handlers.youtube import youtube_handler
from ..utils.language import detect_language


class DocumentQueryTool(AITool):
    """Tool for querying user documents"""
    
    @property
    def name(self) -> str:
        return "Document Query"
    
    @property
    def description(self) -> str:
        return "Search for information in user's documents. Use this when the user asks about their uploaded documents or files."
    
    async def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute document query"""
        try:
            if not context or 'user_id' not in context:
                return {"error": "User ID required for document query"}
            
            user_id = context['user_id']
            
            # Use existing document handler logic
            result = await document_handler.query_documents(query, user_id)
            
            # Format the result for better readability
            if isinstance(result, dict):
                formatted_result = {
                    "answer": result.get("answer", "No relevant information found."),
                    "sources": [
                        f"From {s['metadata'].get('file_name', 'Unknown')}: {s['content'][:200]}..."
                        for s in result.get("sources", [])
                    ],
                    "metadata": {
                        "total_docs": result.get("total_docs", 0),
                        "docs_used": result.get("docs_used", 0)
                    }
                }
                return formatted_result
            return {"answer": "No results found", "sources": []}
            
        except Exception as e:
            return {"error": f"Error querying documents: {str(e)}"}


class LanguageDetectionTool(AITool):
    """Tool for detecting message language"""
    
    @property
    def name(self) -> str:
        return "Language Detection"
    
    @property
    def description(self) -> str:
        return "Detect the language of user messages. Use this to understand what language the user is communicating in."
    
    async def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute language detection"""
        try:
            detected_lang = detect_language(query)
            return {
                "language": detected_lang,
                "original_text": query
            }
        except Exception as e:
            return {"error": f"Error detecting language: {str(e)}"}


class ConversationHistoryTool(AITool):
    """Tool for retrieving conversation history"""
    
    @property
    def name(self) -> str:
        return "Conversation History"
    
    @property
    def description(self) -> str:
        return "Retrieve previous conversation history with the user. Use this to maintain context across conversations."
    
    async def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute conversation history retrieval"""
        try:
            if not context or 'user_id' not in context or 'db' not in context:
                return {"error": "User ID and database connection required"}
            
            user_id = context['user_id']
            db = context['db']
            
            # Get recent messages from MongoDB
            recent_messages = list(db.message_queue.find(
                {
                    "user_id": user_id,
                    "is_processed": True,
                    "response": {"$exists": True}
                }
            ).sort("timestamp", -1).limit(5))
            
            # Format conversation history
            history = []
            for msg in reversed(recent_messages):
                history.append({
                    "user": msg['message'],
                    "assistant": msg.get('response', ''),
                    "timestamp": msg.get('timestamp')
                })
            
            return {
                "history": history,
                "count": len(history)
            }
            
        except Exception as e:
            return {"error": f"Error retrieving conversation history: {str(e)}"}


class YouTubeTranscriptTool(AITool):
    """Tool for processing YouTube video transcripts and searching them"""
    
    @property
    def name(self) -> str:
        return "YouTube Transcript"
    
    @property 
    def description(self) -> str:
        return ("Process YouTube video transcripts and search them for relevant content. "
                "Use this when the user provides a YouTube URL or asks about YouTube video content. "
                "Can extract, store, and search video transcripts to answer questions about video content.")
    
    async def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute YouTube transcript processing or search"""
        try:
            if not context or 'user_id' not in context:
                return {"error": "User ID required for YouTube transcript operations"}
            
            user_id = context['user_id']
            
            # Check if query contains a YouTube URL
            youtube_url_pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)'
            url_match = re.search(youtube_url_pattern, query)
            
            if url_match:
                # Process YouTube URL
                video_url = url_match.group(0)
                if not video_url.startswith('http'):
                    video_url = 'https://' + video_url
                
                result = await youtube_handler.process_youtube_url(user_id, video_url)
                
                if "error" in result:
                    return result
                
                return {
                    "action": "video_processed",
                    "message": f"✅ Successfully processed YouTube video: {result.get('title', 'Unknown')}",
                    "video_info": {
                        "title": result.get('title'),
                        "video_id": result.get('video_id'),
                        "chunks_count": result.get('chunks_count', 0)
                    },
                    "sources": [f"Processed YouTube video transcript with {result.get('chunks_count', 0)} chunks"]
                }
            else:
                # Search existing transcripts
                search_result = await youtube_handler.search_transcripts(user_id, query, limit=5)
                
                if "error" in search_result:
                    return search_result
                
                results = search_result.get('results', [])
                if not results:
                    return {
                        "action": "search_completed",
                        "message": "No relevant YouTube transcript content found for your query.",
                        "sources": []
                    }
                
                # Format search results
                answer_parts = []
                sources = []
                
                for result in results:
                    answer_parts.append(f"From '{result['title']}' at {result['timestamp']}: {result['text']}")
                    sources.append(result['context'])
                
                return {
                    "action": "search_completed", 
                    "answer": "\n\n".join(answer_parts),
                    "sources": sources,
                    "metadata": {
                        "total_results": len(results),
                        "query": query
                    }
                }
                
        except Exception as e:
            return {"error": f"Error with YouTube transcript tool: {str(e)}"}


# Tool registry for easy access
AVAILABLE_TOOLS = {
    "document_query": DocumentQueryTool,
    "language_detection": LanguageDetectionTool,
    "conversation_history": ConversationHistoryTool,
    "youtube_transcript": YouTubeTranscriptTool,
}


def create_tool(tool_name: str) -> Optional[AITool]:
    """Factory function to create tools by name"""
    tool_class = AVAILABLE_TOOLS.get(tool_name)
    if tool_class:
        return tool_class()
    return None


def get_available_tool_names() -> list[str]:
    """Get list of available tool names"""
    return list(AVAILABLE_TOOLS.keys())
