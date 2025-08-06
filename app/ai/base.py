"""
Core AI agent interface and base classes for the DocExpert system.

This module provides the foundation for creating modular AI agents that can be
easily extended with new tools and capabilities.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class AIResponse:
    """Standard response format for AI operations"""
    content: str
    metadata: Optional[Dict[str, Any]] = None
    sources: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.sources is None:
            self.sources = []


class AITool(ABC):
    """Abstract base class for AI tools"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description for the AI agent"""
        pass
    
    @abstractmethod
    async def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute the tool with given query and context"""
        pass


class ConversationAgent(ABC):
    """Abstract base class for conversation agents"""
    
    @abstractmethod
    async def process_message(
        self, 
        message: str, 
        user_id: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AIResponse:
        """Process a user message and return an AI response"""
        pass
    
    @abstractmethod
    def add_tool(self, tool: AITool) -> None:
        """Add a tool to the agent"""
        pass
    
    @abstractmethod
    def remove_tool(self, tool_name: str) -> bool:
        """Remove a tool by name"""
        pass
    
    @abstractmethod
    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        pass


class MemoryManager(ABC):
    """Abstract base class for managing conversation memory"""
    
    @abstractmethod
    async def get_memory(self, user_id: str) -> Any:
        """Get memory for a user"""
        pass
    
    @abstractmethod
    async def update_memory(self, user_id: str, message: str, response: str) -> None:
        """Update memory with new conversation"""
        pass
    
    @abstractmethod
    async def clear_memory(self, user_id: str) -> None:
        """Clear memory for a user"""
        pass
