import logging
from typing import Optional

from lumino.api_sdk.models import (
    FineTuningJobCreate,
    FineTuningJobResponse,
    FineTuningJobDetailResponse,
    ListResponse,
    Pagination
)
from lumino.api_sdk.sdk import LuminoSDK


class FineTuningEndpoint:
    """
    Handles fine-tuning job-related API endpoints for the Lumino SDK.
    """

    def __init__(self, sdk: LuminoSDK):
        """
        Initialize the FineTuningEndpoint.

        Args:
            sdk (Any): The LuminoSDK instance.
        """
        self._sdk = sdk
        self.logger = logging.getLogger(__name__)

    async def create_fine_tuning_job(self, job_create: FineTuningJobCreate) -> FineTuningJobResponse:
        """
        Create a new fine-tuning job.

        Args:
            job_create (FineTuningJobCreate): The fine-tuning job creation data.

        Returns:
            FineTuningJobResponse: The created fine-tuning job information.

        Raises:
            LuminoAPIError: If the API request fails.
            LuminoValidationError: If the provided data is invalid.
        """
        self.logger.info("Creating fine-tuning job: %s", job_create.name)
        data = await self._sdk.request("POST", "/fine-tuning", json=job_create.model_dump())
        return FineTuningJobResponse(**data)

    async def list_fine_tuning_jobs(self, page: int = 1, items_per_page: int = 20,
                                    status: Optional[str] = None) -> ListResponse:
        """
        List all fine-tuning jobs.

        Args:
            page (int): The page number to retrieve. Defaults to 1.
            items_per_page (int): The number of items per page. Defaults to 20.
            status (Optional[str]): Filter jobs by status. If None, all jobs are returned.

        Returns:
            ListResponse: A list of fine-tuning jobs and pagination information.

        Raises:
            LuminoAPIError: If the API request fails.
        """
        self.logger.info("Listing fine-tuning jobs (page %d)", page)
        params = {"page": page, "items_per_page": items_per_page}
        if status:
            params["status"] = status
        data = await self._sdk.request("GET", "/fine-tuning", params=params)
        return ListResponse(
            data=[FineTuningJobResponse(**item) for item in data['data']],
            pagination=Pagination(**data['pagination'])
        )

    async def get_fine_tuning_job(self, job_name: str) -> FineTuningJobDetailResponse:
        """
        Get detailed information about a specific fine-tuning job.

        Args:
            job_name (str): The name of the fine-tuning job.

        Returns:
            FineTuningJobDetailResponse: Detailed information about the fine-tuning job.

        Raises:
            LuminoAPIError: If the API request fails.
        """
        self.logger.info("Getting fine-tuning job: %s", job_name)
        data = await self._sdk.request("GET", f"/fine-tuning/{job_name}")
        return FineTuningJobDetailResponse(**data)

    async def cancel_fine_tuning_job(self, job_name: str) -> FineTuningJobDetailResponse:
        """
        Cancel a fine-tuning job.

        Args:
            job_name (str): The name of the fine-tuning job to cancel.

        Returns:
            FineTuningJobDetailResponse: Updated information about the cancelled fine-tuning job.

        Raises:
            LuminoAPIError: If the API request fails.
        """
        self.logger.info("Cancelling fine-tuning job: %s", job_name)
        data = await self._sdk.request("POST", f"/fine-tuning/{job_name}/cancel")
        return FineTuningJobDetailResponse(**data)

    async def delete_fine_tuning_job(self, job_name: str) -> None:
        """
        Delete a fine-tuning job.

        Args:
            job_name (str): The name of the fine-tuning job to delete.

        Raises:
            LuminoAPIError: If the API request fails.
        """
        self.logger.info("Deleting fine-tuning job: %s", job_name)
        await self._sdk.request("DELETE", f"/fine-tuning/{job_name}")
        self.logger.info("Deleted fine-tuning job: %s", job_name)
