"""
AI Service for handling message processing with modular AI components.

This service acts as a bridge between the Telegram handlers and the AI system,
providing a clean interface for message processing.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from .agent import conversation_agent
from .base import AIResponse
from ..database.mongodb import db
from ..utils.logging import get_logger
from ..handlers.document import document_handler

# Setup logger
service_logger = get_logger('ai_service')


class AIMessageService:
    """Service for processing messages with AI agents"""
    
    def __init__(self):
        self.agent = conversation_agent
        self.db = db
    
    async def process_user_messages(
        self, 
        messages: List[Dict[str, Any]], 
        user_id: str
    ) -> str:
        """Process a batch of user messages and return response"""
        service_logger.info(f"🚀 Processing {len(messages)} messages for user {user_id}")
        
        try:
            # Combine messages
            combined_message = " ".join([msg["message"] for msg in messages])
            service_logger.debug(f"📝 Combined message: {combined_message[:200]}...")
            
            # Get document context
            doc_context = await self._get_document_context(combined_message, user_id)
            
            # Build context for the agent
            context = {
                'user_id': user_id,
                'db': self.db,
                'document_context': doc_context.get('context', ''),
                'sources': doc_context.get('sources', []),
                'available_docs': doc_context.get('available_docs', [])
            }
            
            # Process with AI agent
            ai_response = await self.agent.process_message(
                combined_message, 
                user_id, 
                context
            )
            
            # Update database with conversation info
            await self._update_conversation_history(messages, ai_response, doc_context)
            
            service_logger.info(f"✅ Successfully processed messages for user {user_id}")
            return ai_response.content
            
        except Exception as e:
            service_logger.error(f"❌ Error processing messages: {str(e)}")
            return "Sorry, I couldn't process your message. Please try again."
    
    async def _get_document_context(self, query: str, user_id: str) -> Dict[str, Any]:
        """Get relevant context from user's documents"""
        try:
            # Get user's documents from MongoDB
            user_docs = self.db.get_user_documents(user_id)
            if not user_docs:
                return {"context": "", "sources": [], "available_docs": []}

            # Format available documents info
            available_docs = []
            for doc in user_docs:
                metadata = doc.get('metadata', {})
                file_name = metadata.get('file_name', '')
                upload_time = doc.get('upload_time', datetime.utcnow()).strftime('%Y-%m-%d %H:%M')
                status = "✅" if doc.get('status') == "processed" else "❌"
                available_docs.append(f"- {status} {file_name} (Uploaded: {upload_time})")

            # Query documents with multiple variations for better results
            semantic_variations = [
                query,  # Original query
                f"find information about {query}",
                f"what does the document say about {query}",
                query.replace("?", "").strip()  # Clean query
            ]
            
            all_responses = []
            for variation in semantic_variations:
                response = await document_handler.query_documents(variation, user_id, k=5)
                if response and response.get("answer"):
                    all_responses.append(response)

            # Build context
            context_parts = []
            
            # Add available documents list
            context_parts.append("Your available documents:")
            context_parts.extend(available_docs)
            context_parts.append("")  # Empty line for separation

            # Add query-specific content if available
            for response in all_responses:
                if response.get("answer"):
                    context_parts.append("Relevant content:")
                    context_parts.append(response["answer"])
                    context_parts.append("")

            # Combine all sources
            all_sources = []
            for response in all_responses:
                if response.get("sources"):
                    all_sources.extend(response["sources"])

            return {
                "context": "\n".join(context_parts),
                "sources": all_sources,
                "available_docs": available_docs,
                "stats": {
                    "total_docs": len(user_docs),
                    "semantic_variations_used": len(all_responses),
                    "total_chunks_used": len(all_sources)
                }
            }

        except Exception as e:
            service_logger.error(f"❌ Error getting document context: {str(e)}")
            return {"context": "", "sources": [], "available_docs": [], "stats": {}}
    
    async def _update_conversation_history(
        self, 
        messages: List[Dict[str, Any]], 
        ai_response: AIResponse, 
        doc_context: Dict[str, Any]
    ) -> None:
        """Update conversation history in database"""
        try:
            if not messages:
                return
            
            combined_message = " ".join([msg["message"] for msg in messages])
            
            # Update the last message with conversation history
            self.db.message_queue.update_one(
                {"_id": messages[-1]["_id"]},
                {
                    "$set": {
                        "conversation_history": {
                            "user_message": combined_message,
                            "assistant_response": ai_response.content,
                            "language": ai_response.metadata.get('language', 'unknown'),
                            "document_context_used": bool(doc_context.get('sources')),
                            "documents_referenced": [
                                source["metadata"]["file_name"]
                                for source in doc_context.get("sources", [])
                                if isinstance(source, dict) and source.get("metadata", {}).get("file_name")
                            ],
                            "stats": doc_context.get('stats', {}),
                            "timestamp": datetime.utcnow(),
                            "error": ai_response.error
                        }
                    }
                }
            )
            
            service_logger.debug("📊 Updated conversation history in database")
            
        except Exception as e:
            service_logger.error(f"❌ Error updating conversation history: {str(e)}")
    
    def add_tool_to_agent(self, tool_name: str) -> bool:
        """Add a tool to the conversation agent"""
        from .tools import create_tool
        
        tool = create_tool(tool_name)
        if tool:
            self.agent.add_tool(tool)
            service_logger.info(f"➕ Added tool '{tool_name}' to agent")
            return True
        
        service_logger.warning(f"⚠️ Tool '{tool_name}' not found")
        return False
    
    def remove_tool_from_agent(self, tool_name: str) -> bool:
        """Remove a tool from the conversation agent"""
        success = self.agent.remove_tool(tool_name)
        if success:
            service_logger.info(f"➖ Removed tool '{tool_name}' from agent")
        else:
            service_logger.warning(f"⚠️ Tool '{tool_name}' not found for removal")
        return success
    
    def get_agent_tools(self) -> List[str]:
        """Get list of available agent tools"""
        return self.agent.get_available_tools()
    
    async def clear_user_memory(self, user_id: str) -> None:
        """Clear conversation memory for a user"""
        await self.agent.memory_manager.clear_memory(user_id)
        service_logger.info(f"🗑️ Cleared memory for user {user_id}")


# Create singleton instance
ai_service = AIMessageService()
