import logging
from datetime import date

from lumino.api_sdk.exceptions import LuminoClientError
from lumino.api_sdk.models import (
    CreditHistoryResponse,
    ListResponse,
    Pagination
)
from lumino.api_sdk.sdk import LuminoSDK


class BillingEndpoint:
    """
    Handles billing-related API endpoints for the Lumino SDK.
    """

    def __init__(self, sdk: LuminoSDK):
        """
        Initialize the BillingEndpoint.

        Args:
            sdk (Any): The LuminoSDK instance.
        """
        self._sdk = sdk
        self.logger = logging.getLogger(__name__)

    async def get_credit_history(
            self,
            start_date: date,
            end_date: date,
            page: int = 1,
            items_per_page: int = 20
    ) -> ListResponse:
        """
        Get credit history for the current user.

        Args:
            start_date (date): The start date for the period (YYYY-MM-DD).
            end_date (date): The end date for the period (YYYY-MM-DD).
            page (int): The page number to retrieve. Defaults to 1.
            items_per_page (int): The number of items per page. Defaults to 20.

        Returns:
            ListResponse: A list of credit history entries and pagination information.

        Raises:
            LuminoAPIError: If the API request fails.
        """
        if start_date > end_date:
            raise LuminoClientError("end_date must be equal to or after start_date")

        self.logger.info(f"Getting credit history from {start_date} to {end_date} (page {page})")
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "page": page,
            "items_per_page": items_per_page
        }
        data = await self._sdk.request("GET", "/billing/credit-history", params=params)
        return ListResponse(
            data=[CreditHistoryResponse(**item) for item in data['data']],
            pagination=Pagination(**data['pagination'])
        )
