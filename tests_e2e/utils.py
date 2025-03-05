import asyncio
import random
import re
import string
import time
from datetime import datetime
from functools import wraps
from typing import Any, Callable, TypeVar, ParamSpec

from logger import get_logger

logger = get_logger(__name__)

P = ParamSpec('P')
T = TypeVar('T')


def retry(
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        exceptions: tuple = (Exception,)
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """
    Retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry

    Returns:
        Decorated function that will retry on specified exceptions
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            current_delay = delay
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts - 1:  # Last attempt
                        raise  # Re-raise the last exception
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed: {str(e)}"
                        f"Retrying in {current_delay:.1f} seconds..."
                    )
                    time.sleep(current_delay)
                    current_delay *= backoff
            return await func(*args, **kwargs)  # Final attempt

        return wrapper

    return decorator


def generate_test_name(prefix: str = "test") -> str:
    """
    Generate a unique test resource name with timestamp and random suffix.

    Args:
        prefix: Prefix for the generated name

    Returns:
        Generated name in format: prefix-YYYYMMDD-HHMMSS-XXXXX
        where XXXXX is a random string
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
    return f"{prefix}-{timestamp}-{suffix}"


def sanitize_name(name: str) -> str:
    """
    Sanitize a name to be used as a resource identifier.

    Args:
        name: Name to sanitize

    Returns:
        Sanitized name with only lowercase letters, numbers, and hyphens
    """
    # Convert to lowercase and replace spaces/special chars with hyphens
    name = name.lower()
    name = re.sub(r'[^a-z0-9-]', '-', name)
    # Remove consecutive hyphens
    name = re.sub(r'-+', '-', name)
    # Remove leading/trailing hyphens
    name = name.strip('-')
    return name


def format_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.23 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


async def wait_for_condition(
        condition: Callable,
        timeout: float = None,
        interval: float = 1.0,
        message: str = "Condition not met"
) -> None:
    """
    Wait for a condition to be met with timeout.

    Args:
        condition: Function that returns True when condition is met
        timeout: Maximum time to wait in seconds (None for config default)
        interval: Time between checks in seconds
        message: Error message if timeout is reached

    Raises:
        TimeoutError: If condition is not met within timeout period
    """
    start_time = time.time()
    while True:
        r = await condition()
        if r:
            return
        if time.time() - start_time > timeout:
            raise TimeoutError(f"{message} within {timeout} seconds")
        await asyncio.sleep(interval)


def is_valid_uuid(uuid_str: str) -> bool:
    """
    Check if a string is a valid UUID.

    Args:
        uuid_str: String to check

    Returns:
        True if string is a valid UUID, False otherwise
    """
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    )
    return bool(uuid_pattern.match(uuid_str.lower()))


class TestData:
    """
    Class to store and manage test data between test cases.
    Thread-safe singleton to share data across test modules.
    """
    _instance = None
    _data: dict[str, Any] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def set(self, key: str, value: Any) -> None:
        """Set a test data value."""
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a test data value."""
        return self._data.get(key, default)

    def clear(self) -> None:
        """Clear all test data."""
        self._data.clear()

    def __contains__(self, key: str) -> bool:
        """Check if key exists in test data."""
        return key in self._data


if __name__ == "__main__":
    # Example usage
    test_name = generate_test_name("resource")
    print(f"Generated test name: {test_name}")

    sanitized = sanitize_name("My Test Resource!@#")
    print(f"Sanitized name: {sanitized}")

    size = format_size(1234567)
    print(f"Formatted size: {size}")

    # Test data example
    test_data = TestData()
    test_data.set("user_id", "123")
    print(f"Test data: {test_data.get('user_id')}")
