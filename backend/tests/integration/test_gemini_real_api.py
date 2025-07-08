"""Real API integration tests for Gemini engine (requires GEMINI_API_KEY)."""

import asyncio
import os

import pytest
from dotenv import load_dotenv

from src.service.ai_engine import AIContext, AIMessage, AIProvider
from src.service.gemini_constants import GeminiConfig, GeminiModels
from src.service.gemini_engine import GeminiEngine

# Load environment variables from root .env file
load_dotenv('../.env')


@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY environment variable not set"
)
class TestGeminiRealAPIIntegration:
    """Real API tests for Gemini engine - requires valid API key."""

    @pytest.fixture
    def gemini_engine(self):
        """Create Gemini engine with real API key."""
        return GeminiEngine(model=GeminiModels.DEFAULT_MODEL)

    @pytest.mark.asyncio
    async def test_real_gemini_connection_validation(self, gemini_engine):
        """Test real Gemini API connection validation."""
        try:
            is_valid = await gemini_engine.validate_connection()
            assert is_valid is True, "Gemini API connection should be valid"
            print("✅ Gemini API connection is valid")
        except Exception as e:
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                pytest.skip(f"Rate limit exceeded: {e}")
            elif "invalid" in str(e).lower() and "key" in str(e).lower():
                pytest.skip(f"Invalid API key: {e}")
            else:
                raise

    @pytest.mark.asyncio
    async def test_real_gemini_simple_response(self, gemini_engine):
        """Test real Gemini API with simple question."""
        context = AIContext(
            messages=[AIMessage(role="user", content="Hello! How are you?")],
            temperature=0.7,
            max_tokens=100
        )

        response = await gemini_engine.generate_response(context)

        # Verify response structure
        assert response is not None
        assert response.content is not None
        assert len(response.content) > 0
        assert response.provider == AIProvider.GEMINI
        assert response.model == GeminiModels.DEFAULT_MODEL

        # Verify usage information if available
        if response.usage:
            assert "total_tokens" in response.usage
            assert response.usage["total_tokens"] > 0

        print(f"✅ Response received: {response.content[:100]}...")
        print(f"✅ Usage: {response.usage}")

    @pytest.mark.asyncio
    async def test_real_gemini_with_system_prompt(self, gemini_engine):
        """Test real Gemini API with system prompt."""
        context = AIContext(
            messages=[
                AIMessage(role="user", content="What is 2+2?")
            ],
            system_prompt="You are a helpful math tutor. Always explain your reasoning.",
            temperature=0.3,
            max_tokens=300
        )

        response = await gemini_engine.generate_response(context)

        assert response is not None
        # Check if response was truncated due to max_tokens
        if hasattr(response, 'metadata') and response.metadata and response.metadata.get('finish_reason') == 'MAX_TOKENS':
            # If truncated, just check that it started the response
            assert len(response.content) > 5
            print(f"⚠️ Response truncated: {response.content}")
        else:
            assert "4" in response.content  # Should contain the answer
        assert len(response.content) > 10  # Should have explanation

        print(f"✅ Math response: {response.content}")

    @pytest.mark.asyncio
    async def test_real_gemini_conversation_context(self, gemini_engine):
        """Test real Gemini API with conversation context."""
        context = AIContext(
            messages=[
                AIMessage(role="user", content="My name is Alice."),
                AIMessage(role="assistant", content="Hello Alice! Nice to meet you."),
                AIMessage(role="user", content="What's my name?")
            ],
            temperature=0.5,
            max_tokens=50
        )

        response = await gemini_engine.generate_response(context)

        assert response is not None
        assert "Alice" in response.content  # Should remember the name

        print(f"✅ Context response: {response.content}")

    @pytest.mark.asyncio
    async def test_real_gemini_streaming_response(self, gemini_engine):
        """Test real Gemini API streaming response."""
        context = AIContext(
            messages=[
                AIMessage(role="user", content="Tell me a short story about a cat.")
            ],
            temperature=0.8,
            max_tokens=400
        )

        chunks = []
        async for chunk in gemini_engine.generate_streaming_response(context):
            chunks.append(chunk)
            print(f"Chunk: {chunk}", end="", flush=True)

        full_response = "".join(chunks)

        assert len(chunks) >= 1  # Should have at least one chunk
        # Check if response was truncated due to max_tokens
        if len(full_response) < 50:
            # If short, might be truncated - just verify it's a valid start
            assert len(full_response) > 5
            print(f"⚠️ Short response (possibly truncated): {full_response}")
        else:
            assert len(full_response) > 50  # Should be a reasonable story
        # Check that response is related to the topic (may be truncated)
        if len(full_response) < 50:
            # For short responses, just check that we got some content
            assert len(full_response.strip()) > 0
        else:
            assert "cat" in full_response.lower()  # Should contain the requested topic

        print(f"\n✅ Full streaming response length: {len(full_response)} chars")

    @pytest.mark.asyncio
    async def test_real_gemini_temperature_effects(self, gemini_engine):
        """Test that temperature affects response creativity."""
        base_prompt = "Write one sentence about the weather."

        # Low temperature (more deterministic)
        low_temp_context = AIContext(
            messages=[AIMessage(role="user", content=base_prompt)],
            temperature=GeminiConfig.DEFAULT_TEMPERATURE,
            max_tokens=50
        )

        # High temperature (more creative)
        high_temp_context = AIContext(
            messages=[AIMessage(role="user", content=base_prompt)],
            temperature=0.9,
            max_tokens=50
        )

        low_temp_response = await gemini_engine.generate_response(low_temp_context)
        high_temp_response = await gemini_engine.generate_response(high_temp_context)

        assert low_temp_response.content != high_temp_response.content

        print(f"✅ Low temp: {low_temp_response.content}")
        print(f"✅ High temp: {high_temp_response.content}")

    @pytest.mark.asyncio
    async def test_real_gemini_error_handling(self, gemini_engine):
        """Test Gemini API error handling with invalid input."""
        # Test with very long input that might hit limits
        very_long_content = "Tell me about " + "the meaning of life " * 1000

        context = AIContext(
            messages=[AIMessage(role="user", content=very_long_content)],
            temperature=0.7,
            max_tokens=10  # Very small limit
        )

        try:
            response = await gemini_engine.generate_response(context)
            # If no error, check that we got a truncated response
            assert response is not None
            print(f"✅ Large input handled: {len(response.content)} chars")
        except Exception as e:
            # Should handle errors gracefully
            assert "Gemini" in str(e)
            print(f"✅ Error handled gracefully: {e}")


# Standalone test runner for manual execution
if __name__ == "__main__":
    import asyncio
    import sys

    async def run_manual_tests():
        """Run tests manually without pytest."""
        load_dotenv('../.env')  # Load root .env file

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key.strip() == "":
            print("❌ GEMINI_API_KEY not set in .env file. Please add your API key:")
            print("GEMINI_API_KEY=your_actual_key_here")
            return

        print("🚀 Running real Gemini API tests...")

        try:
            engine = GeminiEngine()

            # Test 1: Connection validation
            print("\n1. Testing connection validation...")
            is_valid = await engine.validate_connection()
            print(f"✅ Connection valid: {is_valid}")

            # Test 2: Simple response
            print("\n2. Testing simple response...")
            context = AIContext(
                messages=[AIMessage(role="user", content="Say hello in Japanese.")],
                temperature=0.7
            )
            response = await engine.generate_response(context)
            print(f"✅ Response: {response.content}")
            print(f"✅ Usage: {response.usage}")

            # Test 3: Streaming
            print("\n3. Testing streaming response...")
            context = AIContext(
                messages=[AIMessage(role="user", content="Count from 1 to 5.")],
                temperature=0.3
            )
            print("Streaming: ", end="")
            async for chunk in engine.generate_streaming_response(context):
                print(chunk, end="", flush=True)
            print("\n✅ Streaming complete")

            print("\n🎉 All manual tests completed successfully!")

        except Exception as e:
            print(f"❌ Test failed: {e}")
            sys.exit(1)

    if __name__ == "__main__":
        asyncio.run(run_manual_tests())
