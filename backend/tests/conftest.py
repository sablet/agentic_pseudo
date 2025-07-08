"""Test constants and configuration for Gemini AI engine testing."""

import os
import pytest


class GeminiTestConfig:
    """Test-specific configuration constants."""

    # Test settings for validation
    TEST_TEMPERATURE = 0.1
    TEST_MAX_TOKENS = 10

    # Test generation config
    TEST_GENERATION_CONFIG = {
        "temperature": TEST_TEMPERATURE,
        "max_output_tokens": TEST_MAX_TOKENS,
    }


class GeminiErrorCodes:
    """Gemini-specific error codes for testing."""

    # Authentication errors
    MISSING_API_KEY = "missing_api_key"
    INVALID_API_KEY = "invalid_api_key"
    AUTH_FAILED = "auth_failed"

    # Rate limiting errors
    QUOTA_EXCEEDED = "quota_exceeded"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"

    # Generation errors
    EMPTY_RESPONSE = "empty_response"
    GENERATION_FAILED = "generation_failed"
    STREAMING_FAILED = "streaming_failed"

    # Validation errors
    INVALID_MODEL = "invalid_model"
    INVALID_PARAMETERS = "invalid_parameters"


@pytest.fixture
def gemini_test_config():
    """Fixture providing test configuration."""
    return GeminiTestConfig()


@pytest.fixture
def gemini_error_codes():
    """Fixture providing error codes for testing."""
    return GeminiErrorCodes()


@pytest.fixture(autouse=True)
def setup_test_database():
    """Setup test database configuration."""
    # Set test database URL for all tests
    original_db_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
    
    yield
    
    # Restore original database URL
    if original_db_url:
        os.environ["DATABASE_URL"] = original_db_url
    else:
        os.environ.pop("DATABASE_URL", None)
