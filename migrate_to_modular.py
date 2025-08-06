#!/usr/bin/env python3
"""
Migration script for transitioning to the modular AI architecture.

This script helps migrate from the monolithic MessageHandler to the
new modular AI system with minimal disruption.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    required_modules = [
        'langchain',
        'langchain_xai', 
        'telegram',
        'fastapi',
        'motor',
        'pymongo'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} (missing)")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_modules)}")
        print("Install them with: pip install " + " ".join(missing_modules))
        return False
    
    print("✅ All dependencies available")
    return True


def check_environment():
    """Check if required environment variables are set"""
    print("\n🔍 Checking environment variables...")
    
    required_env_vars = [
        'TELEGRAM_BOT_TOKEN',
        'XAI_API_KEY',
        'MONGODB_URI'
    ]
    
    missing_vars = []
    
    for var in required_env_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}")
        else:
            print(f"  ❌ {var} (missing)")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Set them in your .env file or environment")
        return False
    
    print("✅ All environment variables set")
    return True


def test_module_imports():
    """Test importing the new modular components"""
    print("\n🔍 Testing modular component imports...")
    
    test_imports = [
        ('app.ai.base', 'AITool, ConversationAgent, AIResponse'),
        ('app.ai.tools', 'AVAILABLE_TOOLS'),
        ('app.ai.memory', 'memory_manager'),
        ('app.ai.agent', 'conversation_agent'),
        ('app.ai.service', 'ai_service'),
        ('app.telegram.bot', 'telegram_bot'),
        ('app.handlers.telegram_message', 'telegram_message_handler')
    ]
    
    failed_imports = []
    
    for module_name, components in test_imports:
        try:
            exec(f"from {module_name} import {components}")
            print(f"  ✅ {module_name}")
        except ImportError as e:
            print(f"  ❌ {module_name} ({str(e)})")
            failed_imports.append(module_name)
    
    if failed_imports:
        print(f"\n⚠️  Failed imports: {', '.join(failed_imports)}")
        return False
    
    print("✅ All modular components import successfully")
    return True


async def test_ai_service():
    """Test the AI service functionality"""
    print("\n🔍 Testing AI service...")
    
    try:
        from app.ai.service import ai_service
        
        # Test getting available tools
        tools = ai_service.get_agent_tools()
        print(f"  ✅ Available tools: {len(tools)}")
        for tool in tools:
            print(f"    - {tool}")
        
        # Test memory clearing (safe operation)
        await ai_service.clear_user_memory("test_user")
        print("  ✅ Memory management working")
        
        print("✅ AI service tests passed")
        return True
        
    except Exception as e:
        print(f"  ❌ AI service test failed: {str(e)}")
        return False


def check_file_structure():
    """Check if the modular file structure exists"""
    print("\n🔍 Checking file structure...")
    
    required_files = [
        'app/ai/__init__.py',
        'app/ai/base.py',
        'app/ai/tools.py',
        'app/ai/memory.py', 
        'app/ai/agent.py',
        'app/ai/service.py',
        'app/telegram/__init__.py',
        'app/telegram/bot.py',
        'app/handlers/telegram_message.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} (missing)")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {len(missing_files)}")
        return False
    
    print("✅ All required files present")
    return True


async def run_migration_checks():
    """Run all migration checks"""
    print("🚀 DocExpert Modular Architecture Migration Checker")
    print("=" * 60)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Environment", check_environment), 
        ("File Structure", check_file_structure),
        ("Module Imports", test_module_imports),
        ("AI Service", test_ai_service)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        
        if asyncio.iscoroutinefunction(check_func):
            result = await check_func()
        else:
            result = check_func()
            
        results[check_name] = result
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 MIGRATION CHECK SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(results.values())
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {check_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 MIGRATION READY!")
        print("All checks passed. The modular system is ready to use.")
        print("\nNext steps:")
        print("1. Start the application: python main.py")
        print("2. Test with Telegram bot")
        print("3. Monitor logs for any issues")
    else:
        print("\n⚠️  MIGRATION BLOCKED")
        print("Some checks failed. Please resolve the issues above.")
        print("See MODULAR_ARCHITECTURE.md for detailed setup instructions.")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = asyncio.run(run_migration_checks())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Migration check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Migration check failed: {str(e)}")
        sys.exit(1)
