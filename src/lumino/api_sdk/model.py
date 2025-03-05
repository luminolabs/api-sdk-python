import logging

from lumino.api_sdk.models import (
    BaseModelResponse,
    FineTunedModelResponse,
    ListResponse,
    Pagination
)
from lumino.api_sdk.sdk import LuminoSDK


class ModelEndpoint:
    """
    Handles model-related API endpoints for the Lumino SDK.
    """

    def __init__(self, sdk: LuminoSDK):
        """
        Initialize the ModelEndpoint.

        Args:
            sdk (Any): The LuminoSDK instance.
        """
        self._sdk = sdk
        self.logger = logging.getLogger(__name__)

    async def list_base_models(self, page: int = 1, items_per_page: int = 20) -> ListResponse:
        """
        List all available base models.

        Args:
            page (int): The page number to retrieve. Defaults to 1.
            items_per_page (int): The number of items per page. Defaults to 20.

        Returns:
            ListResponse: A list of base models and pagination information.

        Raises:
            LuminoAPIError: If the API request fails.
        """
        self.logger.info("Listing base models (page %d)", page)
        params = {"page": page, "items_per_page": items_per_page}
        data = await self._sdk.request("GET", "/models/base", params=params)
        return ListResponse(
            data=[BaseModelResponse(**item) for item in data['data']],
            pagination=Pagination(**data['pagination'])
        )

    async def get_base_model(self, model_name: str) -> BaseModelResponse:
        """
        Get information about a specific base model.

        Args:
            model_name (str): The name of the base model.

        Returns:
            BaseModelResponse: Information about the base model.

        Raises:
            LuminoAPIError: If the API request fails.
        """
        self.logger.info("Getting base model: %s", model_name)
        data = await self._sdk.request("GET", f"/models/base/{model_name}")
        return BaseModelResponse(**data)

    async def list_fine_tuned_models(self, page: int = 1, items_per_page: int = 20) -> ListResponse:
        """
        List all fine-tuned models.

        Args:
            page (int): The page number to retrieve. Defaults to 1.
            items_per_page (int): The number of items per page. Defaults to 20.

        Returns:
            ListResponse: A list of fine-tuned models and pagination information.

        Raises:
            LuminoAPIError: If the API request fails.
        """
        self.logger.info("Listing fine-tuned models (page %d)", page)
        params = {"page": page, "items_per_page": items_per_page}
        data = await self._sdk.request("GET", "/models/fine-tuned", params=params)
        return ListResponse(
            data=[FineTunedModelResponse(**item) for item in data['data']],
            pagination=Pagination(**data['pagination'])
        )

    async def get_fine_tuned_model(self, model_name: str) -> FineTunedModelResponse:
        """
        Get information about a specific fine-tuned model.

        Args:
            model_name (str): The name of the fine-tuned model.

        Returns:
            FineTunedModelResponse: Information about the fine-tuned model.

        Raises:
            LuminoAPIError: If the API request fails.
        """
        self.logger.info("Getting fine-tuned model: %s", model_name)
        data = await self._sdk.request("GET", f"/models/fine-tuned/{model_name}")
        return FineTunedModelResponse(**data)
