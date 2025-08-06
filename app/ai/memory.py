"""
Memory management for AI conversations.

This module handles conversation memory, context storage, and retrieval
for different users and sessions.
"""

from typing import Dict, Any, Optional
from langchain.memory import ConversationBufferMemory
from .base import MemoryManager
from ..database.mongodb import db
from ..utils.logging import get_logger

# Setup logger
memory_logger = get_logger('ai_memory')


class LangChainMemoryManager(MemoryManager):
    """LangChain-based memory manager for conversation history"""
    
    def __init__(self):
        self.memories: Dict[str, ConversationBufferMemory] = {}
        self.db = db
    
    async def get_memory(self, user_id: str) -> ConversationBufferMemory:
        """Get or create memory for a user"""
        if user_id not in self.memories:
            memory_logger.debug(f"🧠 Creating new memory for user {user_id}")
            self.memories[user_id] = ConversationBufferMemory(
                return_messages=True,
                input_key="input",
                output_key="output"
            )
            
            # Load recent conversation history from database
            await self._load_history_from_db(user_id)
        
        return self.memories[user_id]
    
    async def update_memory(self, user_id: str, message: str, response: str) -> None:
        """Update memory with new conversation"""
        memory = await self.get_memory(user_id)
        memory.chat_memory.add_user_message(message)
        memory.chat_memory.add_ai_message(response)
        
        memory_logger.debug(f"💭 Updated memory for user {user_id}")
    
    async def clear_memory(self, user_id: str) -> None:
        """Clear memory for a user"""
        if user_id in self.memories:
            self.memories[user_id].clear()
            memory_logger.info(f"🗑️ Cleared memory for user {user_id}")
    
    async def _load_history_from_db(self, user_id: str) -> None:
        """Load recent conversation history from database"""
        try:
            recent_messages = list(self.db.message_queue.find(
                {
                    "user_id": user_id,
                    "is_processed": True,
                    "response": {"$exists": True}
                }
            ).sort("timestamp", -1).limit(5))
            
            memory = self.memories[user_id]
            
            # Add messages to memory in chronological order
            for msg in reversed(recent_messages):
                memory.chat_memory.add_user_message(msg['message'])
                if msg.get('response'):
                    memory.chat_memory.add_ai_message(msg['response'])
            
            memory_logger.debug(f"📚 Loaded {len(recent_messages)} messages from DB for user {user_id}")
            
        except Exception as e:
            memory_logger.error(f"❌ Failed to load history for user {user_id}: {str(e)}")
    
    def get_conversation_history(self, user_id: str) -> list[str]:
        """Get formatted conversation history for a user"""
        if user_id not in self.memories:
            return []
        
        memory = self.memories[user_id]
        history = []
        
        for message in memory.chat_memory.messages:
            if hasattr(message, 'content'):
                if message.__class__.__name__ == 'HumanMessage':
                    history.append(f"User: {message.content}")
                elif message.__class__.__name__ == 'AIMessage':
                    history.append(f"Assistant: {message.content}")
        
        return history


# Create a singleton instance
memory_manager = LangChainMemoryManager()
