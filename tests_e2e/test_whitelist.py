import asyncio
from typing import TYPE_CHECKING

from logger import get_logger
from lumino.api_sdk.models import WhitelistRequestCreate
from utils import TestData, generate_test_name

if TYPE_CHECKING:
    from test_runner import TestRunner

logger = get_logger(__name__)
test_data = TestData()


async def test_whitelist_operations(runner: 'TestRunner') -> None:
    """
    Test whitelist operations.

    Tests:
    - Submit a whitelist request
    - Get current whitelist status
    """
    logger.info("Starting whitelist operations test")

    # Generate test data for the whitelist request
    test_name = generate_test_name("whitelist-user")
    test_email = f"{test_name}@example.com"
    test_phone = "1234567890"

    # Create a whitelist request
    logger.info(f"Submitting whitelist request for {test_name}")
    
    whitelist_request = WhitelistRequestCreate(
        name=test_name,
        email=test_email,
        phone_number=test_phone
    )
    
    whitelist = await runner.sdk.whitelist.request_to_be_whitelisted(whitelist_request)
    
    # Store the whitelist request ID for potential cleanup
    test_data.set('test_whitelist_id', str(whitelist.id))
    
    # Verify the whitelist request was created successfully
    assert whitelist.name == test_name, f"Whitelist name mismatch. Expected: {test_name}, got: {whitelist.name}"
    assert whitelist.email == test_email, f"Whitelist email mismatch"
    assert whitelist.phone_number == test_phone, f"Whitelist phone number mismatch"
    assert whitelist.is_whitelisted is False, "New whitelist request should not be pre-approved"
    assert whitelist.has_signed_nda is False, "New whitelist request should not have NDA signed"
    
    logger.info(f"Successfully created whitelist request with ID: {whitelist.id}")
    
    # Retrieve whitelist status
    logger.info("Retrieving whitelist status")
    status = await runner.sdk.whitelist.get_whitelist_status()
    
    # Verify the retrieved status matches what we created
    assert status.id == whitelist.id, "Whitelist ID mismatch in status response"
    assert status.name == test_name, "Whitelist name mismatch in status response"
    assert status.is_whitelisted is False, "Whitelist approval status mismatch"
    assert status.has_signed_nda is False, "NDA status mismatch"
    
    logger.info("Whitelist operations test completed successfully")


async def test_duplicate_whitelist_request(runner: 'TestRunner') -> None:
    """
    Test that submitting a duplicate whitelist request fails appropriately.
    This test should run after test_whitelist_operations.
    """
    logger.info("Starting duplicate whitelist request test")
    
    # Generate new test data
    test_name = generate_test_name("duplicate-whitelist")
    test_email = f"{test_name}@example.com"
    test_phone = "9876543210"
    
    whitelist_request = WhitelistRequestCreate(
        name=test_name,
        email=test_email,
        phone_number=test_phone
    )
    
    try:
        # This should fail since a whitelist request already exists for this user
        await runner.sdk.whitelist.request_to_be_whitelisted(whitelist_request)
        # If we get here, the test failed
        assert False, "Duplicate whitelist request should have been rejected"
    except Exception as e:
        # Verify the error is about a duplicate request
        logger.info(f"Received expected error for duplicate request: {str(e)}")
        assert "already has a whitelist request" in str(e).lower(), "Unexpected error message"
    
    logger.info("Duplicate whitelist request test completed successfully")


if __name__ == "__main__":
    # For manual testing
    from test_runner import TestRunner

    async def run_test():
        runner = TestRunner()
        try:
            await runner.setup()
            await test_whitelist_operations(runner)
            await test_duplicate_whitelist_request(runner)
        finally:
            await runner.cleanup()

    asyncio.run(run_test())