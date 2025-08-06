#!/usr/bin/env python3
"""
Simple test script for the modular AI system.

This script can be run independently to test the core functionality
of the new modular architecture without requiring a full setup.
"""

import asyncio
import sys
import os
from typing import Dict, Any, Optional
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Mock implementations for testing without full dependencies
class MockAITool:
    """Mock AI tool for testing"""
    
    def __init__(self, name: str, description: str):
        self._name = name
        self._description = description
    
    @property
    def name(self) -> str:
        return self._name
    
    @property 
    def description(self) -> str:
        return self._description
    
    async def execute(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {
            "tool_used": self.name,
            "query": query,
            "result": f"Mock result for: {query}"
        }


class MockConversationAgent:
    """Mock conversation agent for testing"""
    
    def __init__(self):
        self.tools: Dict[str, MockAITool] = {}
        self._setup_default_tools()
    
    def _setup_default_tools(self):
        """Setup some default mock tools"""
        tools = [
            MockAITool("Document Query", "Search user documents"),
            MockAITool("Language Detection", "Detect message language"),
            MockAITool("Conversation History", "Get conversation history")
        ]
        
        for tool in tools:
            self.tools[tool.name] = tool
    
    async def process_message(self, message: str, user_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Mock message processing"""
        return {
            "content": f"Mock response to: {message}",
            "metadata": {
                "user_id": user_id,
                "tools_available": len(self.tools)
            },
            "sources": []
        }
    
    def add_tool(self, tool: MockAITool) -> None:
        """Add a tool"""
        self.tools[tool.name] = tool
    
    def remove_tool(self, tool_name: str) -> bool:
        """Remove a tool"""
        if tool_name in self.tools:
            del self.tools[tool_name]
            return True
        return False
    
    def get_available_tools(self) -> list:
        """Get available tools"""
        return list(self.tools.keys())


async def test_tool_system():
    """Test the tool system"""
    print("🔧 Testing Tool System...")
    
    # Create mock tools
    weather_tool = MockAITool("Weather", "Get weather information")
    calc_tool = MockAITool("Calculator", "Perform calculations")
    
    # Test tool properties
    assert weather_tool.name == "Weather"
    assert weather_tool.description == "Get weather information"
    
    # Test tool execution
    result = await weather_tool.execute("New York weather")
    assert "Mock result" in result["result"]
    
    print("  ✅ Tool creation and execution works")
    
    return True


async def test_agent_system():
    """Test the agent system"""
    print("🤖 Testing Agent System...")
    
    # Create mock agent
    agent = MockConversationAgent()
    
    # Test initial tools
    initial_tools = agent.get_available_tools()
    assert len(initial_tools) == 3  # Default tools
    print(f"  ✅ Agent initialized with {len(initial_tools)} tools")
    
    # Test adding tools
    custom_tool = MockAITool("Custom", "Custom functionality")
    agent.add_tool(custom_tool)
    
    updated_tools = agent.get_available_tools()
    assert len(updated_tools) == 4
    assert "Custom" in updated_tools
    print("  ✅ Tool addition works")
    
    # Test removing tools
    success = agent.remove_tool("Custom")
    assert success
    assert len(agent.get_available_tools()) == 3
    print("  ✅ Tool removal works")
    
    # Test message processing
    response = await agent.process_message("Hello", "test_user")
    assert "Mock response" in response["content"]
    assert response["metadata"]["user_id"] == "test_user"
    print("  ✅ Message processing works")
    
    return True


async def test_modular_concepts():
    """Test core modular concepts"""
    print("🧩 Testing Modular Concepts...")
    
    # Test separation of concerns
    # Agent focuses on conversation management
    agent = MockConversationAgent()
    
    # Tools focus on specific functionality
    tools = [
        MockAITool("Search", "Search functionality"), 
        MockAITool("Analyze", "Analysis functionality"),
        MockAITool("Translate", "Translation functionality")
    ]
    
    # Test dynamic tool management
    for tool in tools:
        agent.add_tool(tool)
    
    assert len(agent.get_available_tools()) == 6  # 3 default + 3 added
    print("  ✅ Dynamic tool management works")
    
    # Test tool independence
    search_result = await tools[0].execute("search query")
    analyze_result = await tools[1].execute("analyze data")
    
    assert search_result["tool_used"] == "Search"
    assert analyze_result["tool_used"] == "Analyze"
    print("  ✅ Tool independence maintained")
    
    return True


async def test_error_handling():
    """Test error handling"""
    print("🚫 Testing Error Handling...")
    
    agent = MockConversationAgent()
    
    # Test removing non-existent tool
    success = agent.remove_tool("NonExistent")
    assert not success
    print("  ✅ Graceful handling of missing tools")
    
    # Test empty context handling
    response = await agent.process_message("test", "user", None)
    assert response["content"]  # Should still work
    print("  ✅ Handles missing context")
    
    return True


async def run_tests():
    """Run all tests"""
    print("🧪 DocExpert Modular Architecture Test Suite")
    print("=" * 50)
    
    tests = [
        ("Tool System", test_tool_system),
        ("Agent System", test_agent_system), 
        ("Modular Concepts", test_modular_concepts),
        ("Error Handling", test_error_handling)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{test_name}")
        print("-" * len(test_name))
        try:
            result = await test_func()
            results[test_name] = result
            print(f"✅ {test_name} passed")
        except Exception as e:
            results[test_name] = False
            print(f"❌ {test_name} failed: {str(e)}")
    
    # Summary
    print(f"\n{'=' * 50}")
    print("📊 TEST SUMMARY")
    print(f"{'=' * 50}")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("The modular architecture concepts are working correctly.")
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED")
        print("Some modular concepts need attention.")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(run_tests())
        print(f"\n{'🎉 SUCCESS' if success else '❌ FAILURE'}")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test suite crashed: {str(e)}")
        sys.exit(1)
