"""
Telegram-focused message handler that delegates AI processing to the AI service.

This handler is focused on Telegram-specific message management and uses
the modular AI service for actual message processing.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import asyncio

from ..config import WAIT_TIME, MAX_MESSAGES_PER_BATCH
from ..database.mongodb import db
from ..utils.logging import get_logger
from ..ai.service import ai_service

# Setup dedicated logger for message pipeline
msg_logger = get_logger('telegram_message_handler')


class TelegramMessageHandler:
    """Telegram-focused message handler using modular AI service"""
    
    def __init__(self):
        self.db = db
        self.ai_service = ai_service
    
    async def process_message_queue(self, user_id: str) -> str:
        """Process messages in the queue for a user"""
        msg_logger.info(f"📥 Processing message queue for user {user_id}")
        
        try:
            # Wait for additional messages (batching)
            await asyncio.sleep(WAIT_TIME)
            
            # Get cutoff time
            current_time = datetime.utcnow()
            cutoff_time = current_time - timedelta(minutes=5)
            
            # Get pending messages
            messages = self.db.get_pending_messages(user_id, cutoff_time, MAX_MESSAGES_PER_BATCH)
            
            if not messages:
                msg_logger.debug(f"📭 No pending messages for user {user_id}")
                return ""
            
            msg_logger.info(f"📊 Found {len(messages)} pending messages for user {user_id}")
            
            # Generate batch ID and mark messages as being processed
            batch_id = str(datetime.utcnow())
            message_ids = [msg["_id"] for msg in messages]
            
            self.db.mark_messages_as_processed(message_ids, batch_id)
            msg_logger.debug(f"🏷️ Marked messages as processed with batch ID: {batch_id}")
            
            # Process messages with AI service
            response = await self.ai_service.process_user_messages(messages, user_id)
            
            # Update messages with response
            self.db.update_message_response(batch_id, response)
            msg_logger.info(f"✅ Successfully processed and stored response for user {user_id}")
            
            return response
            
        except Exception as e:
            msg_logger.error(f"❌ Error processing messages for user {user_id}: {str(e)}")
            
            # Mark messages with error if we have message_ids
            if 'message_ids' in locals():
                self.db.message_queue.update_many(
                    {"_id": {"$in": message_ids}},
                    {
                        "$set": {
                            "processing_error": str(e),
                            "error_timestamp": datetime.utcnow()
                        }
                    }
                )
            
            # Return a user-friendly error message
            return "Sorry, I encountered an error while processing your message. Please try again."
    
    async def add_ai_tool(self, tool_name: str) -> bool:
        """Add an AI tool to the service"""
        return self.ai_service.add_tool_to_agent(tool_name)
    
    async def remove_ai_tool(self, tool_name: str) -> bool:
        """Remove an AI tool from the service"""
        return self.ai_service.remove_tool_from_agent(tool_name)
    
    def get_available_ai_tools(self) -> List[str]:
        """Get list of available AI tools"""
        return self.ai_service.get_agent_tools()
    
    async def clear_user_memory(self, user_id: str) -> None:
        """Clear conversation memory for a user"""
        await self.ai_service.clear_user_memory(user_id)
        msg_logger.info(f"🗑️ Cleared conversation memory for user {user_id}")


# Create a singleton instance
telegram_message_handler = TelegramMessageHandler()
