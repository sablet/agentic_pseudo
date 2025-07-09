"""Simple real Gemini API test."""

import asyncio
import os
import sys

from dotenv import load_dotenv

# Load environment variables from root
sys.path.append('..')
load_dotenv('../.env')

from src.service.ai_engine import AIContext, AIMessage
from src.service.gemini_engine import GeminiEngine


async def main():
    """Test real Gemini API."""

    print("🚀 Testing real Gemini API...")
    print(f"API Key: {os.getenv('GEMINI_API_KEY')[:20]}...")

    try:
        # Initialize engine
        engine = GeminiEngine()
        print(f"✅ Engine initialized: {engine.provider} - {engine.model}")

        # Test 1: Connection validation
        print("\n1. Testing connection validation...")
        is_valid = await engine.validate_connection()
        print(f"✅ Connection valid: {is_valid}")

        if not is_valid:
            print("❌ Connection validation failed - stopping tests")
            return

        # Test 2: Simple response
        print("\n2. Testing simple response...")
        context = AIContext(
            messages=[AIMessage(role="user", content="Hello! Please respond with exactly 'Hello World' in Japanese.")],
            temperature=0.3,
            max_tokens=50
        )

        response = await engine.generate_response(context)
        print(f"✅ Response: {response.content}")
        print(f"✅ Provider: {response.provider}")
        print(f"✅ Model: {response.model}")
        print(f"✅ Usage: {response.usage}")

        # Test 3: Math question
        print("\n3. Testing math question...")
        math_context = AIContext(
            messages=[AIMessage(role="user", content="What is 15 + 27? Please provide only the number.")],
            temperature=0.1,
            max_tokens=10
        )

        math_response = await engine.generate_response(math_context)
        print(f"✅ Math response: {math_response.content}")

        # Test 4: Streaming response
        print("\n4. Testing streaming response...")
        stream_context = AIContext(
            messages=[AIMessage(role="user", content="Count from 1 to 5, one number per line.")],
            temperature=0.3,
            max_tokens=50
        )

        print("Streaming output:")
        chunks = []
        async for chunk in engine.generate_streaming_response(stream_context):
            print(chunk, end="", flush=True)
            chunks.append(chunk)

        full_response = "".join(chunks)
        print(f"\n✅ Streaming complete. Total length: {len(full_response)} chars")

        # Test 5: Conversation context
        print("\n5. Testing conversation context...")
        conversation_context = AIContext(
            messages=[
                AIMessage(role="user", content="My favorite color is blue."),
                AIMessage(role="assistant", content="That's nice! Blue is a beautiful color."),
                AIMessage(role="user", content="What's my favorite color?")
            ],
            temperature=0.5,
            max_tokens=30
        )

        conv_response = await engine.generate_response(conversation_context)
        print(f"✅ Conversation response: {conv_response.content}")

        print("\n🎉 All real API tests completed successfully!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
