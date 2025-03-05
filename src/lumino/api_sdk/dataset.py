import logging

import aiohttp

from lumino.api_sdk.models import (
    DatasetCreate,
    DatasetUpdate,
    DatasetResponse,
    ListResponse,
    Pagination
)
from lumino.api_sdk.sdk import LuminoSDK


class DatasetEndpoint:
    """
    Handles dataset-related API endpoints for the Lumino SDK.
    """

    def __init__(self, sdk: LuminoSDK):
        """
        Initialize the DatasetEndpoint.

        Args:
            sdk (Any): The LuminoSDK instance.
        """
        self._sdk = sdk
        self.logger = logging.getLogger(__name__)

    async def upload_dataset(self, file_path: str, dataset_create: DatasetCreate) -> DatasetResponse:
        """
        Upload a new dataset.

        Args:
            file_path (str): The path to the dataset file.
            dataset_create (DatasetCreate): The dataset creation data.

        Returns:
            DatasetResponse: The uploaded dataset information.

        Raises:
            LuminoAPIError: If the API request fails.
            LuminoValidationError: If the provided data is invalid.
            FileNotFoundError: If the specified file does not exist.
        """
        self.logger.info("Uploading dataset: %s", dataset_create.name)
        try:
            with open(file_path, 'rb') as file:
                data = aiohttp.FormData()
                data.add_field('file', file)
                data.add_field('name', dataset_create.name)
                if dataset_create.description:
                    data.add_field('description', dataset_create.description)

                response_data = await self._sdk.request("POST", "/datasets", data=data)
                return DatasetResponse(**response_data)
        except FileNotFoundError:
            self.logger.error("File not found: %s", file_path)
            raise

    async def list_datasets(self, page: int = 1, items_per_page: int = 20) -> ListResponse:
        """
        List all datasets.

        Args:
            page (int): The page number to retrieve. Defaults to 1.
            items_per_page (int): The number of items per page. Defaults to 20.

        Returns:
            ListResponse: A list of datasets and pagination information.

        Raises:
            LuminoAPIError: If the API request fails.
        """
        self.logger.info("Listing datasets (page %d)", page)
        params = {"page": page, "items_per_page": items_per_page}
        data = await self._sdk.request("GET", "/datasets", params=params)
        return ListResponse(
            data=[DatasetResponse(**item) for item in data['data']],
            pagination=Pagination(**data['pagination'])
        )

    async def get_dataset(self, dataset_name: str) -> DatasetResponse:
        """
        Get information about a specific dataset.

        Args:
            dataset_name (str): The name of the dataset.

        Returns:
            DatasetResponse: The dataset information.

        Raises:
            LuminoAPIError: If the API request fails.
        """
        self.logger.info("Getting dataset: %s", dataset_name)
        data = await self._sdk.request("GET", f"/datasets/{dataset_name}")
        return DatasetResponse(**data)

    async def update_dataset(self, dataset_name: str, dataset_update: DatasetUpdate) -> DatasetResponse:
        """
        Update a dataset.

        Args:
            dataset_name (str): The name of the dataset to update.
            dataset_update (DatasetUpdate): The updated dataset information.

        Returns:
            DatasetResponse: The updated dataset information.

        Raises:
            LuminoAPIError: If the API request fails.
            LuminoValidationError: If the provided data is invalid.
        """
        self.logger.info("Updating dataset: %s", dataset_name)
        data = await self._sdk.request(
            "PATCH",
            f"/datasets/{dataset_name}",
            json=dataset_update.model_dump(exclude_unset=True)
        )
        return DatasetResponse(**data)

    async def delete_dataset(self, dataset_name: str) -> None:
        """
        Delete a dataset.

        Args:
            dataset_name (str): The name of the dataset to delete.

        Raises:
            LuminoAPIError: If the API request fails.
        """
        self.logger.info("Deleting dataset: %s", dataset_name)
        await self._sdk.request("DELETE", f"/datasets/{dataset_name}")
