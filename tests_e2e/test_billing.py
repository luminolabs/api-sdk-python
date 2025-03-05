import asyncio
from datetime import date, timedelta
from typing import TYPE_CHECKING

from logger import get_logger
from lumino.api_sdk.models import BillingTransactionType
from utils import TestData

if TYPE_CHECKING:
    from test_runner import TestRunner

logger = get_logger(__name__)
test_data = TestData()


async def test_billing_operations(runner: 'TestRunner') -> None:
    """
    Test billing and credit operations.

    Tests:
    - Get credit history
    - Verify transaction types
    - Check credit balance
    """
    logger.info("Starting billing operations test")

    # Get current user's credit balance
    user = await runner.sdk.user.get_current_user()
    initial_balance = user.credits_balance
    logger.info(f"Current credit balance: {initial_balance}")

    # Set date range for last 90 days of credit history
    end_date = date.today()
    start_date = end_date - timedelta(days=90)
    logger.info(f"Checking credit history from {start_date} to {end_date}")

    # Get credit history
    credit_history = await runner.sdk.billing.get_credit_history(
        start_date,
        end_date
    )
    logger.info(f"Found {len(credit_history.data)} credit transactions")

    # Analyze transactions if any exist
    if credit_history.data:
        # Group transactions by type
        transactions_by_type = {}
        for record in credit_history.data:
            transactions_by_type.setdefault(record.transaction_type, []).append(record)

        # Log summary by type
        for tx_type, records in transactions_by_type.items():
            total_credits = sum(r.credits for r in records)
            logger.info(
                f"{tx_type}: {len(records)} transactions, "
                f"total credits: {total_credits:+.2f}"
            )

        # Verify all transaction types are valid
        for record in credit_history.data:
            assert record.transaction_type in BillingTransactionType, \
                f"Invalid transaction type: {record.transaction_type}"
            assert isinstance(record.credits, (int, float)), \
                f"Invalid credits value: {record.credits}"

    # Test pagination
    page_2 = await runner.sdk.billing.get_credit_history(
        start_date,
        end_date,
        page=2,
        items_per_page=10
    )
    logger.info(
        f"Page 2 contains {len(page_2.data)} transactions, "
        f"total pages: {page_2.pagination.total_pages}"
    )

    # Get updated balance to verify no changes during test
    user = await runner.sdk.user.get_current_user()
    final_balance = user.credits_balance
    assert final_balance == initial_balance, \
        f"Credit balance changed during test: {initial_balance} -> {final_balance}"

    logger.info("Billing operations test completed successfully")


async def verify_credit_transaction(
        runner: 'TestRunner',
        transaction_id: str,
        expected_amount: float,
        transaction_type: BillingTransactionType
) -> None:
    """
    Helper function to verify a specific credit transaction.

    Args:
        runner: TestRunner instance
        transaction_id: ID of the transaction to verify
        expected_amount: Expected credit amount
        transaction_type: Expected transaction type
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=1)

    credit_history = await runner.sdk.billing.get_credit_history(
        start_date,
        end_date
    )

    matching_transactions = [
        t for t in credit_history.data
        if t.transaction_id == transaction_id
           and t.transaction_type == transaction_type
    ]

    assert len(matching_transactions) == 1, \
        f"Expected 1 transaction with ID {transaction_id}, found {len(matching_transactions)}"

    transaction = matching_transactions[0]
    assert abs(transaction.credits - expected_amount) < 0.01, \
        f"Expected credits {expected_amount}, got {transaction.credits}"


if __name__ == "__main__":
    # For manual testing of these modules
    from test_runner import TestRunner


    async def run_test():
        runner = TestRunner()
        try:
            await runner.setup()
            await test_billing_operations(runner)
        finally:
            await runner.cleanup()


    asyncio.run(run_test())
