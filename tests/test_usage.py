from datetime import date
from unittest.mock import patch

import aiohttp
import pytest

from lumino.api_sdk.models import (
    UsageRecordResponse,
    TotalCostResponse,
    ServiceName,
    UsageUnit
)


@pytest.mark.asyncio
async def test_get_total_cost(sdk, mock_response):
    """Test retrieving total cost for a period."""
    cost_data = {
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "total_cost": 150.50
    }
    mock_response.json.return_value = cost_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            end_date = date(2024, 1, 31)
            start_date = date(2024, 1, 1)
            total_cost = await sdk.usage.get_total_cost(start_date, end_date)

            assert isinstance(total_cost, TotalCostResponse)
            assert total_cost.total_cost == 150.50
            assert total_cost.start_date == start_date
            assert total_cost.end_date == end_date


@pytest.mark.asyncio
async def test_get_total_cost_invalid_dates(sdk, mock_response):
    """Test total cost retrieval with invalid date range."""
    async with sdk:
        end_date = date(2024, 1, 1)
        start_date = date(2024, 1, 31)  # Start date after end date

        with pytest.raises(ValueError) as exc_info:
            await sdk.usage.get_total_cost(start_date, end_date)
        assert "end_date must be equal to or after start_date" in str(exc_info.value)


@pytest.mark.asyncio
async def test_list_usage_records(sdk, mock_response):
    """Test listing usage records."""
    usage_data = {
        "data": [{
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "created_at": "2024-01-01T00:00:00Z",
            "service_name": "FINE_TUNING_JOB",
            "usage_amount": 1000000.0,
            "usage_unit": "TOKEN",
            "cost": 50.0,
            "fine_tuning_job_name": "test-job"
        }],
        "pagination": {
            "total_pages": 1,
            "current_page": 1,
            "items_per_page": 20
        }
    }
    mock_response.json.return_value = usage_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            end_date = date(2024, 1, 31)
            start_date = date(2024, 1, 1)
            usage_records = await sdk.usage.list_usage_records(start_date, end_date)

            assert len(usage_records.data) == 1
            assert isinstance(usage_records.data[0], UsageRecordResponse)
            record = usage_records.data[0]
            assert record.service_name == ServiceName.FINE_TUNING_JOB
            assert record.usage_amount == 1000000.0
            assert record.usage_unit == UsageUnit.TOKEN
            assert record.cost == 50.0
            assert record.fine_tuning_job_name == "test-job"


@pytest.mark.asyncio
async def test_list_usage_records_with_service_filter(sdk, mock_response):
    """Test listing usage records with service name filter."""
    usage_data = {
        "data": [{
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "created_at": "2024-01-01T00:00:00Z",
            "service_name": "FINE_TUNING_JOB",
            "usage_amount": 1000000.0,
            "usage_unit": "TOKEN",
            "cost": 50.0,
            "fine_tuning_job_name": "test-job"
        }],
        "pagination": {
            "total_pages": 1,
            "current_page": 1,
            "items_per_page": 20
        }
    }
    mock_response.json.return_value = usage_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            end_date = date(2024, 1, 31)
            start_date = date(2024, 1, 1)
            usage_records = await sdk.usage.list_usage_records(
                start_date,
                end_date,
                service_name="FINE_TUNING_JOB"
            )

            assert len(usage_records.data) == 1
            assert usage_records.data[0].service_name == ServiceName.FINE_TUNING_JOB


@pytest.mark.asyncio
async def test_list_usage_records_invalid_dates(sdk, mock_response):
    """Test usage records listing with invalid date range."""
    async with sdk:
        end_date = date(2024, 1, 1)
        start_date = date(2024, 1, 31)  # Start date after end date

        with pytest.raises(ValueError) as exc_info:
            await sdk.usage.list_usage_records(start_date, end_date)
        assert "end_date must be equal to or after start_date" in str(exc_info.value)


@pytest.mark.asyncio
async def test_list_usage_records_pagination(sdk, mock_response):
    """Test usage records listing with pagination."""
    usage_data = {
        "data": [
            {
                "id": f"123e4567-e89b-12d3-a456-42661417400{i}",
                "created_at": "2024-01-01T00:00:00Z",
                "service_name": "FINE_TUNING_JOB",
                "usage_amount": float(i * 1000000),
                "usage_unit": "TOKEN",
                "cost": float(i * 50),
                "fine_tuning_job_name": f"test-job-{i}"
            } for i in range(3)
        ],
        "pagination": {
            "total_pages": 2,
            "current_page": 1,
            "items_per_page": 3
        }
    }
    mock_response.json.return_value = usage_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            end_date = date(2024, 1, 31)
            start_date = date(2024, 1, 1)
            usage_records = await sdk.usage.list_usage_records(
                start_date,
                end_date,
                page=1,
                items_per_page=3
            )

            assert len(usage_records.data) == 3
            assert usage_records.pagination.total_pages == 2
            assert usage_records.pagination.items_per_page == 3
            assert all(isinstance(record, UsageRecordResponse) for record in usage_records.data)
            assert [record.usage_amount for record in usage_records.data] == [0.0, 1000000.0, 2000000.0]


@pytest.mark.asyncio
async def test_list_usage_records_empty_response(sdk, mock_response):
    """Test usage records listing with empty response."""
    usage_data = {
        "data": [],
        "pagination": {
            "total_pages": 1,
            "current_page": 1,
            "items_per_page": 20
        }
    }
    mock_response.json.return_value = usage_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            end_date = date(2024, 1, 31)
            start_date = date(2024, 1, 1)
            usage_records = await sdk.usage.list_usage_records(start_date, end_date)

            assert len(usage_records.data) == 0
            assert usage_records.pagination.total_pages == 1
            assert usage_records.pagination.current_page == 1
