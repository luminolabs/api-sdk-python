from unittest.mock import patch, mock_open

import aiohttp
import pytest

from lumino.api_sdk.models import (
    DatasetCreate,
    DatasetResponse,
    DatasetStatus, DatasetUpdate
)


@pytest.mark.asyncio
async def test_dataset_operations(sdk, mock_response):
    """Test dataset-related operations."""
    dataset_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "status": "VALIDATED",
        "name": "test-dataset",
        "description": "Test dataset",
        "file_name": "test.jsonl",
        "file_size": 1000,
        "errors": None
    }
    mock_response.json.return_value = dataset_data

    # Mock both the file open operation and the aiohttp request
    mock_file_content = b'{"test": "data"}'
    with patch('builtins.open', mock_open(read_data=mock_file_content)), \
            patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            dataset_create = DatasetCreate(
                name="test-dataset",
                description="Test dataset"
            )
            dataset = await sdk.dataset.upload_dataset("test.jsonl", dataset_create)
            assert isinstance(dataset, DatasetResponse)
            assert dataset.name == "test-dataset"
            assert dataset.status == DatasetStatus.VALIDATED


@pytest.mark.asyncio
async def test_dataset_file_not_found(sdk):
    """Test dataset upload with non-existent file."""
    async with sdk:
        dataset_create = DatasetCreate(
            name="test-dataset",
            description="Test dataset"
        )
        with pytest.raises(FileNotFoundError):
            await sdk.dataset.upload_dataset("nonexistent.jsonl", dataset_create)


@pytest.mark.asyncio
async def test_dataset_list_operations(sdk, mock_response):
    """Test dataset listing operations."""
    datasets_data = {
        "data": [{
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "status": "VALIDATED",
            "name": "test-dataset",
            "description": "Test dataset",
            "file_name": "test.jsonl",
            "file_size": 1000,
            "errors": None
        }],
        "pagination": {
            "total_pages": 1,
            "current_page": 1,
            "items_per_page": 20
        }
    }
    mock_response.json.return_value = datasets_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            datasets = await sdk.dataset.list_datasets()
            assert len(datasets.data) == 1
            assert isinstance(datasets.data[0], DatasetResponse)
            assert datasets.data[0].name == "test-dataset"


@pytest.mark.asyncio
async def test_dataset_get_operations(sdk, mock_response):
    """Test getting a specific dataset."""
    dataset_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "status": "VALIDATED",
        "name": "test-dataset",
        "description": "Test dataset",
        "file_name": "test.jsonl",
        "file_size": 1000,
        "errors": None
    }
    mock_response.json.return_value = dataset_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            dataset = await sdk.dataset.get_dataset("test-dataset")
            assert isinstance(dataset, DatasetResponse)
            assert dataset.name == "test-dataset"
            assert dataset.status == DatasetStatus.VALIDATED


@pytest.mark.asyncio
async def test_dataset_delete_operations(sdk, mock_response):
    """Test dataset deletion."""
    mock_response.json.return_value = None  # DELETE typically returns no content

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            # Should not raise any exception
            await sdk.dataset.delete_dataset("test-dataset")


@pytest.mark.asyncio
async def test_dataset_update_operations(sdk, mock_response):
    """Test dataset update operations."""
    updated_dataset_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "status": "VALIDATED",
        "name": "test-dataset",
        "description": "Updated description",
        "file_name": "test.jsonl",
        "file_size": 1000,
        "errors": None
    }
    mock_response.json.return_value = updated_dataset_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            dataset = await sdk.dataset.update_dataset(
                "test-dataset",
                DatasetUpdate(description="Updated description")
            )
            assert isinstance(dataset, DatasetResponse)
            assert dataset.description == "Updated description"
