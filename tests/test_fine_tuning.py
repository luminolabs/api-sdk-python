from unittest.mock import patch

import aiohttp
import pytest

from lumino.api_sdk.models import (
    FineTuningJobCreate,
    FineTuningJobParameters,
    FineTuningJobResponse,
    FineTuningJobDetailResponse,
    FineTuningJobStatus,
    FineTuningJobType,
    ComputeProvider
)


@pytest.mark.asyncio
async def test_create_fine_tuning_job(sdk, mock_response):
    """Test creation of a fine-tuning job."""
    job_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "base_model_name": "test-base-model",
        "dataset_name": "test-dataset",
        "status": "NEW",
        "name": "test-job",
        "type": "LORA",
        "provider": "GCP",
        "current_step": None,
        "total_steps": None,
        "current_epoch": None,
        "total_epochs": None,
        "num_tokens": None
    }
    mock_response.json.return_value = job_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            job_create = FineTuningJobCreate(
                base_model_name="test-base-model",
                dataset_name="test-dataset",
                name="test-job",
                type=FineTuningJobType.LORA,
                provider=ComputeProvider.GCP,
                parameters=FineTuningJobParameters(
                    batch_size=2,
                    shuffle=True,
                    num_epochs=1
                )
            )
            job = await sdk.fine_tuning.create_fine_tuning_job(job_create)
            assert isinstance(job, FineTuningJobResponse)
            assert job.name == "test-job"
            assert job.status == FineTuningJobStatus.NEW
            assert job.type == FineTuningJobType.LORA
            assert job.provider == ComputeProvider.GCP


@pytest.mark.asyncio
async def test_list_fine_tuning_jobs(sdk, mock_response):
    """Test listing fine-tuning jobs."""
    jobs_data = {
        "data": [{
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "base_model_name": "test-base-model",
            "dataset_name": "test-dataset",
            "status": "RUNNING",
            "name": "test-job",
            "type": "LORA",
            "provider": "GCP",
            "current_step": 100,
            "total_steps": 1000,
            "current_epoch": 1,
            "total_epochs": 3,
            "num_tokens": 50000
        }],
        "pagination": {
            "total_pages": 1,
            "current_page": 1,
            "items_per_page": 20
        }
    }
    mock_response.json.return_value = jobs_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            # Test listing all jobs
            jobs = await sdk.fine_tuning.list_fine_tuning_jobs()
            assert len(jobs.data) == 1
            assert isinstance(jobs.data[0], FineTuningJobResponse)
            assert jobs.data[0].name == "test-job"
            assert jobs.data[0].status == FineTuningJobStatus.RUNNING

            # Test listing with status filter
            jobs = await sdk.fine_tuning.list_fine_tuning_jobs(status="RUNNING")
            assert len(jobs.data) == 1
            assert jobs.data[0].status == FineTuningJobStatus.RUNNING


@pytest.mark.asyncio
async def test_get_fine_tuning_job(sdk, mock_response):
    """Test getting details of a specific fine-tuning job."""
    job_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "base_model_name": "test-base-model",
        "dataset_name": "test-dataset",
        "status": "COMPLETED",
        "name": "test-job",
        "type": "LORA",
        "provider": "GCP",
        "current_step": 1000,
        "total_steps": 1000,
        "current_epoch": 3,
        "total_epochs": 3,
        "num_tokens": 50000,
        "parameters": {
            "batch_size": 2,
            "shuffle": True,
            "num_epochs": 3
        },
        "metrics": {
            "loss": 0.1,
            "accuracy": 0.95
        },
        "timestamps": {
            "started_at": "2024-01-01T00:00:00Z",
            "completed_at": "2024-01-01T01:00:00Z"
        }
    }
    mock_response.json.return_value = job_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            job = await sdk.fine_tuning.get_fine_tuning_job("test-job")
            assert isinstance(job, FineTuningJobDetailResponse)
            assert job.name == "test-job"
            assert job.status == FineTuningJobStatus.COMPLETED
            assert job.parameters["batch_size"] == 2
            assert job.metrics["accuracy"] == 0.95
            assert "started_at" in job.timestamps


@pytest.mark.asyncio
async def test_cancel_fine_tuning_job(sdk, mock_response):
    """Test cancelling a fine-tuning job."""
    job_data = {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z",
        "base_model_name": "test-base-model",
        "dataset_name": "test-dataset",
        "status": "STOPPING",
        "name": "test-job",
        "type": "LORA",
        "provider": "GCP",
        "current_step": 500,
        "total_steps": 1000,
        "current_epoch": 2,
        "total_epochs": 3,
        "num_tokens": 25000,
        "parameters": {
            "batch_size": 2,
            "shuffle": True,
            "num_epochs": 3
        },
        "metrics": {
            "loss": 0.2
        },
        "timestamps": {
            "started_at": "2024-01-01T00:00:00Z",
            "stopping_at": "2024-01-01T00:30:00Z"
        }
    }
    mock_response.json.return_value = job_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            job = await sdk.fine_tuning.cancel_fine_tuning_job("test-job")
            assert isinstance(job, FineTuningJobDetailResponse)
            assert job.status == FineTuningJobStatus.STOPPING
            assert "stopping_at" in job.timestamps


@pytest.mark.asyncio
async def test_delete_fine_tuning_job(sdk, mock_response):
    """Test deleting a fine-tuning job."""
    mock_response.json.return_value = None  # DELETE typically returns no content

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            # Should not raise any exception
            await sdk.fine_tuning.delete_fine_tuning_job("test-job")


@pytest.mark.asyncio
async def test_fine_tuning_job_pagination(sdk, mock_response):
    """Test fine-tuning job listing with pagination."""
    jobs_data = {
        "data": [
            {
                "id": f"123e4567-e89b-12d3-a456-42661417400{i}",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "base_model_name": "test-base-model",
                "dataset_name": "test-dataset",
                "status": status,
                "name": f"test-job-{i}",
                "type": "LORA",
                "provider": "GCP",
                "current_step": None,
                "total_steps": None,
                "current_epoch": None,
                "total_epochs": None,
                "num_tokens": None
            } for i, status in enumerate(["NEW", "RUNNING", "COMPLETED"])
        ],
        "pagination": {
            "total_pages": 2,
            "current_page": 1,
            "items_per_page": 3
        }
    }
    mock_response.json.return_value = jobs_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            jobs = await sdk.fine_tuning.list_fine_tuning_jobs(page=1, items_per_page=3)
            assert len(jobs.data) == 3
            assert jobs.pagination.total_pages == 2
            assert jobs.pagination.items_per_page == 3
            assert all(isinstance(job, FineTuningJobResponse) for job in jobs.data)
            assert [job.status for job in jobs.data] == [
                FineTuningJobStatus.NEW,
                FineTuningJobStatus.RUNNING,
                FineTuningJobStatus.COMPLETED
            ]
