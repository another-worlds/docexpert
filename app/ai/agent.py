"""
LangChain-based conversation agent implementation.

This module contains the main conversation agent that uses LangChain
for processing user messages and generating responses.
"""

from typing import Dict, Any, List, Optional
import asyncio
from langchain_xai import ChatXAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import SystemMessage
from langchain.agents import initialize_agent, Tool, AgentType
from langchain.memory import ConversationBufferMemory

from .base import ConversationAgent, AITool, AIResponse
from .memory import memory_manager
from .tools import AVAILABLE_TOOLS, create_tool
from ..config import LLM_MODEL, LLM_TEMPERATURE, XAI_API_KEY
from ..utils.logging import get_logger
from ..utils.text import normalize_text
from ..utils.language import detect_language

# Setup logger
agent_logger = get_logger('ai_agent')


class LangChainConversationAgent(ConversationAgent):
    """LangChain-based conversation agent"""
    
    def __init__(self):
        self.llm = ChatXAI(
            api_key=XAI_API_KEY,
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE
        )
        self.tools: Dict[str, AITool] = {}
        self.memory_manager = memory_manager
        self.agent = None
        self._setup_default_tools()
        self._setup_agent()
    
    def _setup_default_tools(self):
        """Setup default tools for the agent"""
        # Add document query tool
        doc_tool = create_tool("document_query")
        if doc_tool:
            self.tools[doc_tool.name] = doc_tool
        
        # Add language detection tool
        lang_tool = create_tool("language_detection")
        if lang_tool:
            self.tools[lang_tool.name] = lang_tool
        
        # Add conversation history tool
        hist_tool = create_tool("conversation_history")
        if hist_tool:
            self.tools[hist_tool.name] = hist_tool
        
        # Add YouTube transcript tool
        youtube_tool = create_tool("youtube_transcript")
        if youtube_tool:
            self.tools[youtube_tool.name] = youtube_tool
        
        agent_logger.info(f"🔧 Initialized agent with {len(self.tools)} default tools")
    
    def _setup_agent(self):
        """Setup the LangChain agent"""
        # Convert AI tools to LangChain tools
        langchain_tools = []
        for tool in self.tools.values():
            langchain_tool = Tool(
                name=tool.name,
                func=self._create_sync_wrapper(tool),
                description=tool.description
            )
            langchain_tools.append(langchain_tool)
        
        # Initialize agent
        self.agent = initialize_agent(
            tools=langchain_tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=3,
            memory=ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True
            )
        )
        
        agent_logger.debug("🤖 LangChain agent initialized")
    
    def _create_sync_wrapper(self, tool: AITool):
        """Create a synchronous wrapper for async tools"""
        def sync_wrapper(query: str) -> str:
            try:
                # Get current context (this will be set by process_message)
                context = getattr(self, '_current_context', {})
                
                # Create event loop if needed
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                # Run the async tool
                result = loop.run_until_complete(tool.execute(query, context))
                
                # Format result as string
                if isinstance(result, dict):
                    if 'error' in result:
                        return f"Error: {result['error']}"
                    elif 'answer' in result:
                        return result['answer']
                    else:
                        return str(result)
                return str(result)
                
            except Exception as e:
                agent_logger.error(f"❌ Error in tool {tool.name}: {str(e)}")
                return f"Error executing {tool.name}: {str(e)}"
        
        return sync_wrapper
    
    async def process_message(
        self, 
        message: str, 
        user_id: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """Process a user message and return an AI response"""
        agent_logger.info(f"🚀 Processing message for user {user_id}")
        agent_logger.debug(f"📝 Message: {message[:100]}...")
        
        try:
            # Set current context for tools
            self._current_context = context or {}
            self._current_context['user_id'] = user_id
            
            # Detect language
            detected_lang = detect_language(message)
            agent_logger.info(f"🌍 Detected language: {detected_lang}")
            
            # Normalize text if Turkish
            if detected_lang == 'tr':
                message = normalize_text(message)
                agent_logger.debug("🔄 Applied Turkish text normalization")
            
            # Get memory for user
            memory = await self.memory_manager.get_memory(user_id)
            
            # Build enhanced message with context
            enhanced_message = await self._build_enhanced_message(
                message, user_id, detected_lang, context
            )
            
            # Process with agent
            agent_response = await self.agent.ainvoke({
                "input": enhanced_message,
                "chat_history": memory.chat_memory.messages
            })
            
            response_content = agent_response.get("output", "")
            
            # Update memory
            await self.memory_manager.update_memory(user_id, message, response_content)
            
            # Create AI response
            ai_response = AIResponse(
                content=response_content,
                metadata={
                    "language": detected_lang,
                    "user_id": user_id,
                    "tools_available": len(self.tools)
                }
            )
            
            agent_logger.info(f"✅ Successfully processed message for user {user_id}")
            return ai_response
            
        except Exception as e:
            agent_logger.error(f"❌ Error processing message: {str(e)}")
            return AIResponse(
                content="Sorry, I encountered an error while processing your message. Please try again.",
                error=str(e)
            )
    
    async def _build_enhanced_message(
        self, 
        message: str, 
        user_id: str, 
        language: str, 
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Build enhanced message with context"""
        
        context_parts = []
        
        # Add conversation history
        history = self.memory_manager.get_conversation_history(user_id)
        if history:
            context_parts.append("Previous Conversation:")
            context_parts.extend(history[-6:])  # Last 3 exchanges
            context_parts.append("")
        
        # Add document context if available
        if context and 'document_context' in context:
            context_parts.append("Document Context:")
            context_parts.append(context['document_context'])
            context_parts.append("")
        
        # Build the enhanced message
        enhanced_message = f"""User Question: {message}

Context:
{chr(10).join(context_parts)}

Instructions:
1. Consider the previous conversation context when responding
2. Provide a direct and natural response
3. Don't mention that you're using tools or searching documents
4. Keep the response concise and focused
5. Use a conversational but professional tone
6. Respond in {language} language
7. If information isn't available, say so briefly
"""
        
        return enhanced_message
    
    def add_tool(self, tool: AITool) -> None:
        """Add a tool to the agent"""
        self.tools[tool.name] = tool
        self._setup_agent()  # Reinitialize agent with new tools
        agent_logger.info(f"➕ Added tool: {tool.name}")
    
    def remove_tool(self, tool_name: str) -> bool:
        """Remove a tool by name"""
        if tool_name in self.tools:
            del self.tools[tool_name]
            self._setup_agent()  # Reinitialize agent without the tool
            agent_logger.info(f"➖ Removed tool: {tool_name}")
            return True
        return False
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.tools.keys())


# Create a singleton instance
conversation_agent = LangChainConversationAgent()
