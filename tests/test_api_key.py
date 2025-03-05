from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import aiohttp
import pytest

from lumino.api_sdk.exceptions import LuminoClientError
from lumino.api_sdk.models import (
    ApiKeyCreate,
    ApiKeyUpdate,
    ApiKeyResponse,
    ApiKeyWithSecretResponse,
    ApiKeyStatus
)


@pytest.mark.asyncio
async def test_create_api_key(sdk, mock_response):
    """Test API key creation."""
    api_key_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": "2024-01-01T00:00:00Z",
        "last_used_at": None,
        "expires_at": "2024-02-01T00:00:00Z",
        "status": "ACTIVE",
        "name": "test-key",
        "prefix": "lum_",
        "secret": "test-secret"
    }
    mock_response.json.return_value = api_key_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            expires_at = datetime.now(timezone.utc) + timedelta(days=30)
            api_key_create = ApiKeyCreate(
                name="test-key",
                expires_at=expires_at
            )
            api_key = await sdk.api_keys.create_api_key(api_key_create)
            assert isinstance(api_key, ApiKeyWithSecretResponse)
            assert api_key.name == "test-key"
            assert api_key.status == ApiKeyStatus.ACTIVE
            assert api_key.secret == "test-secret"


@pytest.mark.asyncio
async def test_list_api_keys(sdk, mock_response):
    """Test API key listing operations."""
    api_keys_data = {
        "data": [{
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "created_at": "2024-01-01T00:00:00Z",
            "last_used_at": None,
            "expires_at": "2024-02-01T00:00:00Z",
            "status": "ACTIVE",
            "name": "test-key",
            "prefix": "lum_"
        }],
        "pagination": {
            "total_pages": 1,
            "current_page": 1,
            "items_per_page": 20
        }
    }
    mock_response.json.return_value = api_keys_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            api_keys = await sdk.api_keys.list_api_keys()
            assert len(api_keys.data) == 1
            assert isinstance(api_keys.data[0], ApiKeyResponse)
            assert api_keys.data[0].name == "test-key"
            assert api_keys.pagination.items_per_page == 20
            assert api_keys.pagination.current_page == 1


@pytest.mark.asyncio
async def test_get_api_key(sdk, mock_response):
    """Test getting a specific API key."""
    api_key_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": "2024-01-01T00:00:00Z",
        "last_used_at": None,
        "expires_at": "2024-02-01T00:00:00Z",
        "status": "ACTIVE",
        "name": "test-key",
        "prefix": "lum_"
    }
    mock_response.json.return_value = api_key_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            api_key = await sdk.api_keys.get_api_key("test-key")
            assert isinstance(api_key, ApiKeyResponse)
            assert api_key.name == "test-key"
            assert api_key.status == ApiKeyStatus.ACTIVE


@pytest.mark.asyncio
async def test_update_api_key(sdk, mock_response):
    """Test API key update operations."""
    updated_api_key_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": "2024-01-01T00:00:00Z",
        "last_used_at": None,
        "expires_at": "2024-03-01T00:00:00Z",
        "status": "ACTIVE",
        "name": "updated-key",
        "prefix": "lum_"
    }
    mock_response.json.return_value = updated_api_key_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            new_expiry = datetime.now(timezone.utc) + timedelta(days=60)
            api_key = await sdk.api_keys.update_api_key(
                "test-key",
                ApiKeyUpdate(
                    name="updated-key",
                    expires_at=new_expiry
                )
            )
            assert isinstance(api_key, ApiKeyResponse)
            assert api_key.name == "updated-key"
            assert api_key.status == ApiKeyStatus.ACTIVE


@pytest.mark.asyncio
async def test_revoke_api_key(sdk, mock_response):
    """Test API key revocation."""
    revoked_api_key_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": "2024-01-01T00:00:00Z",
        "last_used_at": None,
        "expires_at": "2024-02-01T00:00:00Z",
        "status": "REVOKED",
        "name": "test-key",
        "prefix": "lum_"
    }
    mock_response.json.return_value = revoked_api_key_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            api_key = await sdk.api_keys.revoke_api_key("test-key")
            assert isinstance(api_key, ApiKeyResponse)
            assert api_key.status == ApiKeyStatus.REVOKED


@pytest.mark.asyncio
async def test_api_key_invalid_expiry(sdk, mock_response):
    """Test API key creation with invalid expiration date."""
    async with sdk:
        with pytest.raises(LuminoClientError):
            expires_at = datetime.now(timezone.utc) - timedelta(days=1)  # Past date
            api_key_create = ApiKeyCreate(
                name="test-key",
                expires_at=expires_at
            )
            await sdk.api_keys.create_api_key(api_key_create)


@pytest.mark.asyncio
async def test_api_key_pagination(sdk, mock_response):
    """Test API key listing with pagination."""
    api_keys_data = {
        "data": [
            {
                "id": f"123e4567-e89b-12d3-a456-42661417400{i}",
                "created_at": "2024-01-01T00:00:00Z",
                "last_used_at": None,
                "expires_at": "2024-02-01T00:00:00Z",
                "status": "ACTIVE",
                "name": f"test-key-{i}",
                "prefix": "lum_"
            } for i in range(3)
        ],
        "pagination": {
            "total_pages": 2,
            "current_page": 1,
            "items_per_page": 3
        }
    }
    mock_response.json.return_value = api_keys_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            api_keys = await sdk.api_keys.list_api_keys(page=1, items_per_page=3)
            assert len(api_keys.data) == 3
            assert api_keys.pagination.total_pages == 2
            assert api_keys.pagination.items_per_page == 3
            assert all(isinstance(key, ApiKeyResponse) for key in api_keys.data)
