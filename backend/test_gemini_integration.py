"""Test script to verify Gemini integration setup."""

import asyncio
import os

# Load environment variables from root directory
import sys

from dotenv import load_dotenv

sys.path.append('..')
load_dotenv('../.env')

async def test_gemini_setup():
    """Test Gemini engine setup and configuration."""

    print("🔍 Checking Gemini API setup...")

    # Check API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key.strip() == "":
        print("❌ GEMINI_API_KEY not found in .env file")
        print("📝 Please add your API key to .env file:")
        print("   GEMINI_API_KEY=your_actual_api_key_here")
        return False

    print(f"✅ GEMINI_API_KEY found: {api_key[:10]}...")

    # Test imports
    try:
        from src.service.ai_engine import AIContext, AIMessage, AIProvider
        from src.service.gemini_engine import GeminiEngine
        print("✅ All imports successful")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    # Test engine initialization
    try:
        engine = GeminiEngine(model="gemini-1.5-flash")
        print("✅ GeminiEngine initialized successfully")
        print(f"   Provider: {engine.provider}")
        print(f"   Model: {engine.model}")
        print(f"   API Key: {engine.api_key[:10]}...")
    except Exception as e:
        print(f"❌ Engine initialization failed: {e}")
        return False

    # Test context creation
    try:
        context = AIContext(
            messages=[AIMessage(role="user", content="Hello, test message")],
            system_prompt="You are a helpful assistant",
            temperature=0.7,
            max_tokens=100
        )
        print("✅ AIContext created successfully")
        print(f"   Messages: {len(context.messages)}")
        print(f"   System prompt: {context.system_prompt[:30]}...")
    except Exception as e:
        print(f"❌ Context creation failed: {e}")
        return False

    # Test message format conversion
    try:
        prompt = engine._convert_messages_to_gemini_format(context)
        print("✅ Message format conversion successful")
        print(f"   Converted prompt length: {len(prompt)} chars")
        print(f"   Prompt preview: {prompt[:100]}...")
    except Exception as e:
        print(f"❌ Message format conversion failed: {e}")
        return False

    print("\n🎉 All setup tests passed!")
    print("\n📋 Next steps:")
    print("1. Verify your GEMINI_API_KEY is valid")
    print("2. Run: uv run python tests/integration/test_gemini_real_api.py")
    print("3. Or run: uv run pytest tests/integration/test_gemini_real_api.py -v")

    return True

async def test_with_real_api():
    """Test with real API if key is available."""
    from src.service.ai_engine import AIContext, AIMessage
    from src.service.gemini_engine import GeminiEngine

    try:
        print("\n🚀 Testing real API connection...")
        engine = GeminiEngine()

        # Simple connection test
        is_valid = await engine.validate_connection()
        if is_valid:
            print("✅ Real API connection successful!")

            # Simple test message
            context = AIContext(
                messages=[AIMessage(role="user", content="Say 'Hello World' in Japanese")],
                temperature=0.5,
                max_tokens=50
            )

            response = await engine.generate_response(context)
            print(f"✅ Response received: {response.content}")
            print(f"✅ Usage: {response.usage}")

        else:
            print("❌ Real API connection failed")

    except Exception as e:
        print(f"❌ Real API test failed: {e}")
        print("💡 This is expected if you don't have a valid API key")

if __name__ == "__main__":
    print("🔧 Gemini Integration Test")
    print("=" * 50)

    # Run setup tests
    success = asyncio.run(test_gemini_setup())

    if success:
        # Ask user if they want to test real API
        try:
            user_input = input("\n❓ Test with real API? (y/n): ").lower().strip()
            if user_input in ['y', 'yes']:
                asyncio.run(test_with_real_api())
        except KeyboardInterrupt:
            print("\n👋 Test cancelled by user")
        except Exception:
            print("\n⚠️  Skipping real API test")

    print("\n✅ Test script completed")
