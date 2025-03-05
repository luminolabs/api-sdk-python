import asyncio
from datetime import date, timedelta
from typing import TYPE_CHECKING

from logger import get_logger
from lumino.api_sdk.models import ServiceName, UsageUnit
from utils import TestData

if TYPE_CHECKING:
    from test_runner import TestRunner

logger = get_logger(__name__)
test_data = TestData()


async def test_usage_operations(runner: 'TestRunner') -> None:
    """
    Test usage tracking operations.

    Tests:
    - Get total cost
    - List usage records
    - Filter by service
    - Date range queries
    """
    logger.info("Starting usage operations test")

    # Set date range for last 30 days
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    logger.info(f"Checking usage from {start_date} to {end_date}")

    # Get total cost
    total_cost = await runner.sdk.usage.get_total_cost(start_date, end_date)
    assert total_cost.total_cost >= 0, f"Invalid total cost: {total_cost.total_cost}"
    logger.info(f"Total cost for period: ${total_cost.total_cost:.2f}")

    # List all usage records
    usage_records = await runner.sdk.usage.list_usage_records(start_date, end_date)
    logger.info(f"Found {len(usage_records.data)} usage records")

    # Check record details if any exist
    if usage_records.data:
        record = usage_records.data[0]
        assert record.usage_amount > 0, f"Invalid usage amount: {record.usage_amount}"
        assert record.cost >= 0, f"Invalid cost: {record.cost}"

        # Verify enums
        assert record.service_name in ServiceName, \
            f"Invalid service name: {record.service_name}"
        assert record.usage_unit in UsageUnit, \
            f"Invalid usage unit: {record.usage_unit}"

    # Test filtering by service
    ft_records = await runner.sdk.usage.list_usage_records(
        start_date,
        end_date,
        service_name=ServiceName.FINE_TUNING_JOB
    )
    logger.info(f"Found {len(ft_records.data)} fine-tuning job records")

    # Test shorter date range (last 7 days)
    recent_end = end_date
    recent_start = end_date - timedelta(days=7)
    recent_records = await runner.sdk.usage.list_usage_records(
        recent_start,
        recent_end
    )
    logger.info(f"Found {len(recent_records.data)} records in last 7 days")

    logger.info("Usage operations test completed successfully")


if __name__ == "__main__":
    # For manual testing
    from test_runner import TestRunner


    async def run_test():
        runner = TestRunner()
        try:
            await runner.setup()
            await test_usage_operations(runner)
        finally:
            await runner.cleanup()


    asyncio.run(run_test())
