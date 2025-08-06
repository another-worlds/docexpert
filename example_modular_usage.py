"""
Example usage of the modular AI system.

This example demonstrates how to use the new modular architecture
to create custom AI tools and agents.
"""

import asyncio
from typing import Dict, Any, Optional
from app.ai.base import AITool
from app.ai.tools import create_tool
from app.ai.service import ai_service


class WeatherTool(AITool):
    """Example custom tool for weather information"""
    
    @property
    def name(self) -> str:
        return "Weather Info"
    
    @property 
    def description(self) -> str:
        return "Get weather information for a location. Use this when users ask about weather."
    
    async def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Mock weather tool implementation"""
        # In a real implementation, this would call a weather API
        return {
            "weather": f"The weather for {query} is sunny and 25°C",
            "location": query,
            "temperature": "25°C",
            "condition": "Sunny"
        }


class CalculatorTool(AITool):
    """Example calculator tool"""
    
    @property
    def name(self) -> str:
        return "Calculator"
    
    @property
    def description(self) -> str:
        return "Perform basic mathematical calculations. Use this for math problems."
    
    async def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Simple calculator implementation"""
        try:
            # This is a very basic implementation - in reality you'd want more robust parsing
            result = eval(query.replace('x', '*').replace('÷', '/'))
            return {
                "calculation": query,
                "result": str(result)
            }
        except Exception as e:
            return {"error": f"Could not calculate: {str(e)}"}


async def demonstrate_modular_system():
    """Demonstrate the modular AI system"""
    
    print("🚀 Demonstrating Modular AI System")
    print("=" * 50)
    
    # 1. Show current available tools
    print("\n📋 Current AI Tools:")
    current_tools = ai_service.get_agent_tools()
    for i, tool in enumerate(current_tools, 1):
        print(f"  {i}. {tool}")
    
    # 2. Add custom tools
    print("\n➕ Adding Custom Tools...")
    weather_tool = WeatherTool()
    calc_tool = CalculatorTool()
    
    # Add tools to the AI service
    ai_service.agent.add_tool(weather_tool)
    ai_service.agent.add_tool(calc_tool)
    
    print(f"   Added: {weather_tool.name}")
    print(f"   Added: {calc_tool.name}")
    
    # 3. Show updated tools list
    print("\n📋 Updated AI Tools:")
    updated_tools = ai_service.get_agent_tools()
    for i, tool in enumerate(updated_tools, 1):
        print(f"  {i}. {tool}")
    
    # 4. Simulate processing messages with new tools
    print("\n💬 Simulating Message Processing...")
    
    # Mock messages for demonstration
    mock_messages = [
        {
            "_id": "msg1",
            "message": "What's the weather like in New York?",
            "timestamp": "2024-01-01T10:00:00Z"
        }
    ]
    
    # Process with AI service (this would normally be called by the Telegram handler)
    try:
        response = await ai_service.process_user_messages(mock_messages, "demo_user")
        print(f"   Response: {response[:100]}...")
    except Exception as e:
        print(f"   Error: {str(e)}")
        print("   (This is expected in demo mode without full database setup)")
    
    # 5. Tool management demonstration
    print("\n🔧 Tool Management Demo:")
    
    # Remove a tool
    success = ai_service.agent.remove_tool("Calculator")
    print(f"   Removed Calculator tool: {success}")
    
    # Show final tools list
    final_tools = ai_service.get_agent_tools()
    print("   Final tools:")
    for i, tool in enumerate(final_tools, 1):
        print(f"     {i}. {tool}")
    
    print("\n✅ Modular System Demonstration Complete!")


if __name__ == "__main__":
    # Run the demonstration
    try:
        asyncio.run(demonstrate_modular_system())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")
        print("This is expected without full environment setup")
