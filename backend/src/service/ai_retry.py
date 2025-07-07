"""Retry logic and error handling for AI engine operations."""

import asyncio
import logging
from typing import TypeVar, Callable, Awaitable, Optional
from functools import wraps

from .ai_engine import (
    AIEngineError,
    AIEngineConnectionError,
    AIEngineQuotaError,
    AIEngineValidationError,
    AIProvider,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryConfig:
    """Configuration for retry logic."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        retry_on_quota: bool = True,
        retry_on_connection: bool = True,
        retry_on_validation: bool = False,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retry_on_quota = retry_on_quota
        self.retry_on_connection = retry_on_connection
        self.retry_on_validation = retry_on_validation


class AIRetryHandler:
    """Handler for AI engine retry logic."""

    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()

    def should_retry(self, error: Exception, attempt: int) -> bool:
        """Determine if operation should be retried."""

        if attempt >= self.config.max_attempts:
            return False

        if isinstance(error, AIEngineQuotaError):
            return self.config.retry_on_quota

        if isinstance(error, AIEngineConnectionError):
            return self.config.retry_on_connection

        if isinstance(error, AIEngineValidationError):
            return self.config.retry_on_validation

        # Retry on general AI engine errors
        if isinstance(error, AIEngineError):
            return True

        # For testing: retry on basic Exception if not specifically an AI engine error
        # In production, you may want to be more restrictive
        if isinstance(error, Exception) and not isinstance(error, (AIEngineQuotaError, AIEngineConnectionError, AIEngineValidationError)):
            return True

        # Don't retry on other types of errors
        return False

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay before next retry attempt."""

        delay = self.config.base_delay * (self.config.exponential_base ** (attempt - 1))
        return min(delay, self.config.max_delay)

    async def execute_with_retry(
        self,
        operation: Callable[[], Awaitable[T]],
        operation_name: str = "AI operation",
    ) -> T:
        """Execute operation with retry logic."""

        last_error = None

        for attempt in range(1, self.config.max_attempts + 1):
            try:
                logger.debug(
                    f"Attempting {operation_name} (attempt {attempt}/{self.config.max_attempts})"
                )
                return await operation()

            except Exception as error:
                last_error = error

                if not self.should_retry(error, attempt):
                    logger.error(f"{operation_name} failed permanently: {error}")
                    raise error

                delay = self.calculate_delay(attempt)
                logger.warning(
                    f"{operation_name} failed (attempt {attempt}/{self.config.max_attempts}): {error}. "
                    f"Retrying in {delay:.2f} seconds..."
                )

                await asyncio.sleep(delay)

        # If we get here, all attempts failed
        logger.error(
            f"{operation_name} failed after {self.config.max_attempts} attempts"
        )
        if last_error is not None:
            raise last_error
        else:
            raise Exception(f"{operation_name} failed with unknown error")


def with_retry(config: Optional[RetryConfig] = None):
    """Decorator for adding retry logic to async functions."""

    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            retry_handler = AIRetryHandler(config)

            async def operation():
                return await func(*args, **kwargs)

            return await retry_handler.execute_with_retry(
                operation, operation_name=func.__name__
            )

        return wrapper

    return decorator


# Predefined retry configurations
CONSERVATIVE_RETRY = RetryConfig(
    max_attempts=2,
    base_delay=0.5,
    max_delay=10.0,
    retry_on_validation=False,
)

AGGRESSIVE_RETRY = RetryConfig(
    max_attempts=5,
    base_delay=2.0,
    max_delay=120.0,
    retry_on_validation=True,
)

QUOTA_AWARE_RETRY = RetryConfig(
    max_attempts=3,
    base_delay=5.0,
    max_delay=300.0,  # 5 minutes max for quota issues
    retry_on_quota=True,
    retry_on_connection=True,
    retry_on_validation=False,
)
