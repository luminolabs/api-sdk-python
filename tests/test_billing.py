from datetime import date, timedelta
from unittest.mock import patch

import aiohttp
import pytest

from lumino.api_sdk.exceptions import LuminoClientError
from lumino.api_sdk.models import (
    CreditHistoryResponse,
    BillingTransactionType,
)


@pytest.mark.asyncio
async def test_get_credit_history(sdk, mock_response):
    """Test retrieving credit history."""
    credit_history_data = {
        "data": [{
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "created_at": "2024-01-01T00:00:00Z",
            "credits": 100.0,
            "transaction_id": "test-transaction",
            "transaction_type": "NEW_USER_CREDIT"
        }],
        "pagination": {
            "total_pages": 1,
            "current_page": 1,
            "items_per_page": 20
        }
    }
    mock_response.json.return_value = credit_history_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            credit_history = await sdk.billing.get_credit_history(start_date, end_date)

            # Verify response structure
            assert len(credit_history.data) == 1
            assert isinstance(credit_history.data[0], CreditHistoryResponse)

            # Verify data content
            credit_record = credit_history.data[0]
            assert credit_record.credits == 100.0
            assert credit_record.transaction_id == "test-transaction"
            assert credit_record.transaction_type == BillingTransactionType.NEW_USER_CREDIT

            # Verify pagination
            assert credit_history.pagination.total_pages == 1
            assert credit_history.pagination.current_page == 1
            assert credit_history.pagination.items_per_page == 20


@pytest.mark.asyncio
async def test_get_credit_history_with_pagination(sdk, mock_response):
    """Test credit history retrieval with pagination."""
    credit_history_data = {
        "data": [
            {
                "id": f"123e4567-e89b-12d3-a456-42661417400{i}",
                "created_at": "2024-01-01T00:00:00Z",
                "credits": float(i * 100),
                "transaction_id": f"test-transaction-{i}",
                "transaction_type": "MANUAL_ADJUSTMENT"
            } for i in range(3)
        ],
        "pagination": {
            "total_pages": 2,
            "current_page": 1,
            "items_per_page": 3
        }
    }
    mock_response.json.return_value = credit_history_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            credit_history = await sdk.billing.get_credit_history(
                start_date,
                end_date,
                page=1,
                items_per_page=3
            )

            # Verify pagination settings
            assert len(credit_history.data) == 3
            assert credit_history.pagination.total_pages == 2
            assert credit_history.pagination.items_per_page == 3

            # Verify all items are proper instances
            assert all(isinstance(record, CreditHistoryResponse) for record in credit_history.data)

            # Verify transaction types
            assert all(record.transaction_type == BillingTransactionType.MANUAL_ADJUSTMENT
                       for record in credit_history.data)


@pytest.mark.asyncio
async def test_get_credit_history_invalid_dates(sdk, mock_response):
    """Test credit history retrieval with invalid date range."""
    async with sdk:
        end_date = date.today() - timedelta(days=30)
        start_date = date.today()  # Start date after end date

        with pytest.raises(LuminoClientError) as exc_info:
            await sdk.billing.get_credit_history(start_date, end_date)
        assert "end_date must be equal to or after start_date" in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_credit_history_all_transaction_types(sdk, mock_response):
    """Test credit history with different transaction types."""
    credit_history_data = {
        "data": [
            {
                "id": f"123e4567-e89b-12d3-a456-42661417400{i}",
                "created_at": "2024-01-01T00:00:00Z",
                "credits": 100.0,
                "transaction_id": f"test-transaction-{i}",
                "transaction_type": transaction_type
            } for i, transaction_type in enumerate([
                "MANUAL_ADJUSTMENT",
                "NEW_USER_CREDIT",
                "FINE_TUNING_JOB",
                "STRIPE_CHECKOUT"
            ])
        ],
        "pagination": {
            "total_pages": 1,
            "current_page": 1,
            "items_per_page": 20
        }
    }
    mock_response.json.return_value = credit_history_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            credit_history = await sdk.billing.get_credit_history(start_date, end_date)

            # Verify all transaction types are present
            transaction_types = {record.transaction_type for record in credit_history.data}
            expected_types = {
                BillingTransactionType.MANUAL_ADJUSTMENT,
                BillingTransactionType.NEW_USER_CREDIT,
                BillingTransactionType.FINE_TUNING_JOB,
                BillingTransactionType.STRIPE_CHECKOUT
            }
            assert transaction_types == expected_types


@pytest.mark.asyncio
async def test_get_credit_history_empty_response(sdk, mock_response):
    """Test credit history retrieval with empty response."""
    credit_history_data = {
        "data": [],
        "pagination": {
            "total_pages": 1,
            "current_page": 1,
            "items_per_page": 20
        }
    }
    mock_response.json.return_value = credit_history_data

    with patch.object(aiohttp.ClientSession, 'request', return_value=mock_response):
        async with sdk:
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            credit_history = await sdk.billing.get_credit_history(start_date, end_date)

            # Verify empty response handling
            assert len(credit_history.data) == 0
            assert credit_history.pagination.total_pages == 1
            assert credit_history.pagination.current_page == 1
