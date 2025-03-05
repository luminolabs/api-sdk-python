from unittest.mock import patch

import aiohttp
import pytest

from lumino.api_sdk.models import (
    BaseModelResponse,
    FineTunedModelResponse,
    BaseModelStatus,
    FineTunedModelStatus
)


@pytest.mark.asyncio
async def test_list_base_models(sdk, mock_response):
    """Test listing base models."""
    base_models_data = {
        "data": [{
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "description": "Test base model",
            "hf_url": "https://huggingface.co/test-model",
            "status": "ACTIVE",
            "name": "test-base-model",
            "meta": {
                "parameters": "7B",
                "architecture": "Llama"
            }
        }],
        "pagination": {
            "total_pages": 1,
            "current_page": 1,
            "items_per_page": 20
        }
    }
    mock_response.json.return_value = base_models_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            models = await sdk.model.list_base_models()
            assert len(models.data) == 1
            assert isinstance(models.data[0], BaseModelResponse)
            assert models.data[0].name == "test-base-model"
            assert models.data[0].status == BaseModelStatus.ACTIVE
            assert models.data[0].meta["parameters"] == "7B"


@pytest.mark.asyncio
async def test_get_base_model(sdk, mock_response):
    """Test getting a specific base model."""
    base_model_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "description": "Test base model",
        "hf_url": "https://huggingface.co/test-model",
        "status": "ACTIVE",
        "name": "test-base-model",
        "meta": {
            "parameters": "7B",
            "architecture": "Llama"
        }
    }
    mock_response.json.return_value = base_model_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            model = await sdk.model.get_base_model("test-base-model")
            assert isinstance(model, BaseModelResponse)
            assert model.name == "test-base-model"
            assert model.status == BaseModelStatus.ACTIVE
            assert model.hf_url == "https://huggingface.co/test-model"
            assert model.meta["architecture"] == "Llama"


@pytest.mark.asyncio
async def test_list_fine_tuned_models(sdk, mock_response):
    """Test listing fine-tuned models."""
    fine_tuned_models_data = {
        "data": [{
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "fine_tuning_job_name": "test-job",
            "status": "ACTIVE",
            "name": "test-fine-tuned-model",
            "artifacts": {
                "model_size": "500MB",
                "training_steps": 1000
            }
        }],
        "pagination": {
            "total_pages": 1,
            "current_page": 1,
            "items_per_page": 20
        }
    }
    mock_response.json.return_value = fine_tuned_models_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            models = await sdk.model.list_fine_tuned_models()
            assert len(models.data) == 1
            assert isinstance(models.data[0], FineTunedModelResponse)
            assert models.data[0].name == "test-fine-tuned-model"
            assert models.data[0].status == FineTunedModelStatus.ACTIVE
            assert models.data[0].fine_tuning_job_name == "test-job"
            assert models.data[0].artifacts["model_size"] == "500MB"


@pytest.mark.asyncio
async def test_get_fine_tuned_model(sdk, mock_response):
    """Test getting a specific fine-tuned model."""
    fine_tuned_model_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "fine_tuning_job_name": "test-job",
        "status": "ACTIVE",
        "name": "test-fine-tuned-model",
        "artifacts": {
            "model_size": "500MB",
            "training_steps": 1000,
            "final_loss": 0.1
        }
    }
    mock_response.json.return_value = fine_tuned_model_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            model = await sdk.model.get_fine_tuned_model("test-fine-tuned-model")
            assert isinstance(model, FineTunedModelResponse)
            assert model.name == "test-fine-tuned-model"
            assert model.status == FineTunedModelStatus.ACTIVE
            assert model.fine_tuning_job_name == "test-job"
            assert model.artifacts["final_loss"] == 0.1


@pytest.mark.asyncio
async def test_base_model_pagination(sdk, mock_response):
    """Test base model listing with pagination."""
    base_models_data = {
        "data": [
            {
                "id": f"123e4567-e89b-12d3-a456-42661417400{i}",
                "description": f"Test base model {i}",
                "hf_url": f"https://huggingface.co/test-model-{i}",
                "status": status,
                "name": f"test-base-model-{i}",
                "meta": {
                    "parameters": f"{i}B",
                    "architecture": "Llama"
                }
            } for i, status in enumerate(["ACTIVE", "INACTIVE", "DEPRECATED"])
        ],
        "pagination": {
            "total_pages": 2,
            "current_page": 1,
            "items_per_page": 3
        }
    }
    mock_response.json.return_value = base_models_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            models = await sdk.model.list_base_models(page=1, items_per_page=3)
            assert len(models.data) == 3
            assert models.pagination.total_pages == 2
            assert models.pagination.items_per_page == 3
            assert all(isinstance(model, BaseModelResponse) for model in models.data)
            assert [model.status for model in models.data] == [
                BaseModelStatus.ACTIVE,
                BaseModelStatus.INACTIVE,
                BaseModelStatus.DEPRECATED
            ]


@pytest.mark.asyncio
async def test_fine_tuned_model_pagination(sdk, mock_response):
    """Test fine-tuned model listing with pagination."""
    fine_tuned_models_data = {
        "data": [
            {
                "id": f"123e4567-e89b-12d3-a456-42661417400{i}",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "fine_tuning_job_name": f"test-job-{i}",
                "status": status,
                "name": f"test-fine-tuned-model-{i}",
                "artifacts": {
                    "model_size": f"{i}00MB",
                    "training_steps": i * 1000
                }
            } for i, status in enumerate(["ACTIVE", "ACTIVE", "DELETED"])
        ],
        "pagination": {
            "total_pages": 2,
            "current_page": 1,
            "items_per_page": 3
        }
    }
    mock_response.json.return_value = fine_tuned_models_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            models = await sdk.model.list_fine_tuned_models(page=1, items_per_page=3)
            assert len(models.data) == 3
            assert models.pagination.total_pages == 2
            assert models.pagination.items_per_page == 3
            assert all(isinstance(model, FineTunedModelResponse) for model in models.data)
            assert [model.status for model in models.data] == [
                FineTunedModelStatus.ACTIVE,
                FineTunedModelStatus.ACTIVE,
                FineTunedModelStatus.DELETED
            ]
