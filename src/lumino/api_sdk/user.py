import logging

from lumino.api_sdk.models import UserUpdate, UserResponse
from lumino.api_sdk.sdk import LuminoSDK


class UserEndpoint:
    """
    Handles user-related API endpoints for the Lumino SDK.
    """

    def __init__(self, sdk: LuminoSDK):
        """
        Initialize the UserEndpoint.

        Args:
            sdk (Any): The LuminoSDK instance.
        """
        self._sdk = sdk
        self.logger = logging.getLogger(__name__)

    async def get_current_user(self) -> UserResponse:
        """
        Get the current user's information.

        Returns:
            UserResponse: The current user's information.

        Raises:
            LuminoAPIError: If the API request fails.
        """
        self.logger.info("Getting current user information")
        data = await self._sdk.request("GET", "/users/me")
        return UserResponse(**data)

    async def update_current_user(self, user_update: UserUpdate) -> UserResponse:
        """
        Update the current user's information.

        Args:
            user_update (UserUpdate): The updated user information.

        Returns:
            UserResponse: The updated user information.

        Raises:
            LuminoAPIError: If the API request fails.
            LuminoValidationError: If the provided data is invalid.
        """
        self.logger.info("Updating current user information")
        data = await self._sdk.request(
            "PATCH",
            "/users/me",
            json=user_update.model_dump(exclude_unset=True)
        )
        return UserResponse(**data)
