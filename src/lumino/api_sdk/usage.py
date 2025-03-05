import logging
from datetime import date
from typing import Optional

from lumino.api_sdk.models import (
    UsageRecordResponse,
    TotalCostResponse,
    ListResponse,
    Pagination
)
from lumino.api_sdk.sdk import LuminoSDK


class UsageEndpoint:
    """
    Handles usage-related API endpoints for the Lumino SDK.
    """

    def __init__(self, sdk: LuminoSDK):
        """
        Initialize the UsageEndpoint.

        Args:
            sdk (Any): The LuminoSDK instance.
        """
        self._sdk = sdk
        self.logger = logging.getLogger(__name__)

    async def get_total_cost(self, start_date: date, end_date: date) -> TotalCostResponse:
        """
        Get the total cost for a given period.

        Args:
            start_date (date): The start date of the period.
            end_date (date): The end date of the period.

        Returns:
            TotalCostResponse: The total cost information for the specified period.

        Raises:
            LuminoAPIError: If the API request fails.
            ValueError: If end_date is before start_date.
        """
        if end_date < start_date:
            raise ValueError("end_date must be equal to or after start_date")

        self.logger.info("Getting total cost from %s to %s", start_date, end_date)
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        data = await self._sdk.request("GET", "/usage/total-cost", params=params)
        return TotalCostResponse(**data)

    async def list_usage_records(self, start_date: date, end_date: date,
                                 page: int = 1, items_per_page: int = 20,
                                 service_name: Optional[str] = None) -> ListResponse:
        """
        List usage records for a given period.

        Args:
            start_date (date): The start date of the period.
            end_date (date): The end date of the period.
            page (int): The page number to retrieve. Defaults to 1.
            items_per_page (int): The number of items per page. Defaults to 20.
            service_name (Optional[str]): Filter records by service name.

        Returns:
            ListResponse: A list of usage records and pagination information.

        Raises:
            LuminoAPIError: If the API request fails.
            ValueError: If end_date is before start_date.
        """
        if end_date < start_date:
            raise ValueError("end_date must be equal to or after start_date")

        self.logger.info("Listing usage records from %s to %s (page %d)", start_date, end_date, page)
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "page": page,
            "items_per_page": items_per_page
        }
        if service_name:
            params["service_name"] = service_name

        data = await self._sdk.request("GET", "/usage/records", params=params)
        return ListResponse(
            data=[UsageRecordResponse(**item) for item in data['data']],
            pagination=Pagination(**data['pagination'])
        )
