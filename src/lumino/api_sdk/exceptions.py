from typing import Any, Optional


class LuminoClientError(Exception):
    """
    Exception raised when attempting to send an invalid value to the Lumino API.
    """
    pass


class LuminoServerError(Exception):
    """Exception raised for errors returned by the Lumino API."""

    def __init__(self, status: int, message: str, details: Optional[Any] = None):
        """
        Initialize the LuminoAPIError.

        Args:
            status (int): The HTTP status code of the error.
            message (str): The error message.
            details (Optional[Any]): Additional error details, if any.
        """
        self.status = status
        self.details = details
        super().__init__(f"Lumino API Error (Status {status}): {message}")
