import asyncio
from typing import TYPE_CHECKING

from logger import get_logger
from lumino.api_sdk.models import UserStatus, UserUpdate
from utils import TestData, generate_test_name, sanitize_name

if TYPE_CHECKING:
    from test_runner import TestRunner

logger = get_logger(__name__)
test_data = TestData()


async def test_user_operations(runner: 'TestRunner') -> None:
    """
    Test user management operations.

    Tests:
    - Get current user info
    - Update username
    - Verify credits balance
    """
    logger.info("Starting user operations test")

    # Store the original user information
    user = await runner.sdk.user.get_current_user()
    test_data.set('original_user', user)

    logger.info(f"Current user: {user.email}")
    assert user.status == UserStatus.ACTIVE, f"User status is {user.status}, expected ACTIVE"
    assert user.credits_balance >= 0, f"User credits balance is negative: {user.credits_balance}"

    # Update user name with timestamp to ensure uniqueness
    new_name = sanitize_name(generate_test_name("test-user"))
    logger.info(f"Updating user name to: {new_name}")

    updated_user = await runner.sdk.user.update_current_user(
        UserUpdate(name=new_name)
    )

    # Verify update was successful
    assert updated_user.name == new_name, (
        f"User name not updated correctly. "
        f"Expected: {new_name}, got: {updated_user.name}"
    )

    # Get user again to verify persistence
    current_user = await runner.sdk.user.get_current_user()
    assert current_user.name == new_name, (
        f"User name update not persisted. "
        f"Expected: {new_name}, got: {current_user.name}"
    )

    # Store test resources for cleanup
    test_data.set('test_user_name', new_name)

    logger.info("User operations test completed successfully")


async def cleanup_user_operations(runner: 'TestRunner') -> None:
    """
    Clean up user operations test files.
    Restores the original username.
    """
    try:
        original_user = test_data.get('original_user')
        if original_user and test_data.get('test_user_name'):
            await runner.sdk.user.update_current_user(
                UserUpdate(name=original_user.name)
            )
            logger.info(f"Restored original user name: {original_user.name}")
    except Exception as e:
        logger.error(f"Error during user operations cleanup: {e}")
        raise


if __name__ == "__main__":
    # For manual testing
    from test_runner import TestRunner


    async def run_test():
        runner = TestRunner()
        try:
            await runner.setup()
            await test_user_operations(runner)
        finally:
            await cleanup_user_operations(runner)
            await runner.cleanup()


    asyncio.run(run_test())
