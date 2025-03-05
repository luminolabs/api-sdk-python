from unittest.mock import patch

import aiohttp
import pytest

from lumino.api_sdk.models import (
    UserUpdate,
    UserResponse,
    UserStatus
)


@pytest.mark.asyncio
async def test_get_current_user(sdk, mock_response):
    """Test getting current user information."""
    user_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "status": "ACTIVE",
        "name": "Test User",
        "email": "test@example.com",
        "credits_balance": 100.0
    }
    mock_response.json.return_value = user_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            user = await sdk.user.get_current_user()
            assert isinstance(user, UserResponse)
            assert user.name == "Test User"
            assert user.email == "test@example.com"
            assert user.status == UserStatus.ACTIVE
            assert user.credits_balance == 100.0


@pytest.mark.asyncio
async def test_update_current_user(sdk, mock_response):
    """Test updating current user information."""
    updated_user_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "status": "ACTIVE",
        "name": "Updated User",
        "email": "test@example.com",
        "credits_balance": 100.0
    }
    mock_response.json.return_value = updated_user_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            updated_user = await sdk.user.update_current_user(
                UserUpdate(name="Updated User")
            )
            assert isinstance(updated_user, UserResponse)
            assert updated_user.name == "Updated User"
            assert updated_user.status == UserStatus.ACTIVE


@pytest.mark.asyncio
async def test_user_with_empty_name_update(sdk, mock_response):
    """Test updating user with empty name."""
    updated_user_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "status": "ACTIVE",
        "name": "Original Name",
        "email": "test@example.com",
        "credits_balance": 100.0
    }
    mock_response.json.return_value = updated_user_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            # Should not raise validation error when name field is None
            user_update = UserUpdate()
            updated_user = await sdk.user.update_current_user(user_update)
            assert isinstance(updated_user, UserResponse)
            assert updated_user.name == "Original Name"


@pytest.mark.asyncio
async def test_user_with_inactive_status(sdk, mock_response):
    """Test handling of inactive user status."""
    inactive_user_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "status": "INACTIVE",
        "name": "Inactive User",
        "email": "test@example.com",
        "credits_balance": 0.0
    }
    mock_response.json.return_value = inactive_user_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            user = await sdk.user.get_current_user()
            assert isinstance(user, UserResponse)
            assert user.status == UserStatus.INACTIVE
            assert user.credits_balance == 0.0


@pytest.mark.asyncio
async def test_user_with_zero_credits(sdk, mock_response):
    """Test user with zero credits balance."""
    user_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "status": "ACTIVE",
        "name": "Test User",
        "email": "test@example.com",
        "credits_balance": 0.0
    }
    mock_response.json.return_value = user_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            user = await sdk.user.get_current_user()
            assert isinstance(user, UserResponse)
            assert user.credits_balance == 0.0


@pytest.mark.asyncio
async def test_user_update_fields_unchanged(sdk, mock_response):
    """Test that non-updated fields remain unchanged."""
    original_user_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "status": "ACTIVE",
        "name": "Original Name",
        "email": "test@example.com",
        "credits_balance": 100.0
    }
    mock_response.json.return_value = original_user_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            # First get the original user data
            original_user = await sdk.user.get_current_user()

            # Update only the name
            updated_user_data = original_user_data.copy()
            updated_user_data["name"] = "Updated Name"
            mock_response.json.return_value = updated_user_data

            updated_user = await sdk.user.update_current_user(
                UserUpdate(name="Updated Name")
            )

            # Verify only name changed, other fields remained the same
            assert updated_user.name != original_user.name
            assert updated_user.email == original_user.email
            assert updated_user.status == original_user.status
            assert updated_user.credits_balance == original_user.credits_balance
            assert updated_user.id == original_user.id
