import asyncio
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

from logger import get_logger
from lumino.api_sdk.models import ApiKeyCreate, ApiKeyUpdate, ApiKeyStatus
from utils import TestData, generate_test_name, sanitize_name

if TYPE_CHECKING:
    from test_runner import TestRunner

logger = get_logger(__name__)
test_data = TestData()


async def test_api_key_operations(runner: 'TestRunner') -> None:
    """
    Test API key management operations.

    Tests:
    - Create API key
    - List API keys
    - Update API key
    - Get API key details
    - Revoke API key
    """
    logger.info("Starting API key operations test")

    # Generate unique names for our test API keys
    key_name = sanitize_name(generate_test_name("test-key"))
    updated_key_name = sanitize_name(generate_test_name("updated-key"))

    # Create API key with 30-day expiration
    expires_at = datetime.now(timezone.utc) + timedelta(days=30)
    logger.info(f"Creating API key: {key_name}")

    new_key = await runner.sdk.api_keys.create_api_key(
        ApiKeyCreate(
            name=key_name,
            expires_at=expires_at
        )
    )

    # Verify creation
    assert new_key.name == key_name, f"API key name mismatch. Expected: {key_name}, got: {new_key.name}"
    assert new_key.status == ApiKeyStatus.ACTIVE, f"API key not active. Status: {new_key.status}"
    assert new_key.secret is not None, "API key secret not provided"

    # Store the API key for later cleanup
    test_data.set('test_api_key_name', key_name)
    logger.info(f"Created API key with prefix: {new_key.prefix}")

    # List API keys and verify our new key is present
    keys_response = await runner.sdk.api_keys.list_api_keys()
    assert any(k.name == key_name for k in keys_response.data), (
        f"Created API key {key_name} not found in list response"
    )

    # Get specific API key
    key_info = await runner.sdk.api_keys.get_api_key(key_name)
    assert key_info.name == key_name, f"API key details name mismatch"
    assert key_info.prefix == new_key.prefix, f"API key prefix mismatch"

    # Update API key
    new_expiry = datetime.now(timezone.utc) + timedelta(days=60)
    logger.info(f"Updating API key {key_name} to {updated_key_name}")

    updated_key = await runner.sdk.api_keys.update_api_key(
        key_name,
        ApiKeyUpdate(
            name=updated_key_name,
            expires_at=new_expiry
        )
    )

    # Verify update
    assert updated_key.name == updated_key_name, (
        f"API key name not updated. Expected: {updated_key_name}, got: {updated_key.name}"
    )
    test_data.set('test_api_key_name', updated_key_name)  # Update stored name

    # Test API key revocation
    logger.info(f"Revoking API key: {updated_key_name}")
    revoked_key = await runner.sdk.api_keys.revoke_api_key(updated_key_name)
    assert revoked_key.status == ApiKeyStatus.REVOKED, (
        f"API key not revoked. Status: {revoked_key.status}"
    )

    # Verify key appears in listing with revoked status
    keys_response = await runner.sdk.api_keys.list_api_keys()
    revoked_keys = [k for k in keys_response.data if k.name == updated_key_name]
    assert len(revoked_keys) == 1, f"Revoked key not found in listing"
    assert revoked_keys[0].status == ApiKeyStatus.REVOKED, (
        f"Key status not updated in listing. Status: {revoked_keys[0].status}"
    )

    logger.info("API key operations test completed successfully")


async def cleanup_api_keys(runner: 'TestRunner') -> None:
    """
    Clean up API keys created during testing.
    Ensures all test API keys are revoked.
    """
    try:
        key_name = test_data.get('test_api_key_name')
        if key_name:
            try:
                # Attempt to revoke the key if it exists and isn't already revoked
                key_info = await runner.sdk.api_keys.get_api_key(key_name)
                if key_info.status == ApiKeyStatus.ACTIVE:
                    await runner.sdk.api_keys.revoke_api_key(key_name)
                    logger.info(f"Revoked test API key: {key_name}")
            except Exception as e:
                logger.warning(f"Error revoking API key {key_name}: {e}")
    except Exception as e:
        logger.error(f"Error during API key cleanup: {e}")
        raise


if __name__ == "__main__":
    # For manual testing
    from test_runner import TestRunner


    async def run_test():
        runner = TestRunner()
        try:
            await runner.setup()
            await test_api_key_operations(runner)
        finally:
            await cleanup_api_keys(runner)
            await runner.cleanup()


    asyncio.run(run_test())
