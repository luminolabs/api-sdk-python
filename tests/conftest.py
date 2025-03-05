from unittest.mock import AsyncMock

import pytest

from lumino.api_sdk.sdk import LuminoSDK


class MockResponse:
    def __init__(self, status=200):
        self._status = status
        self.json = AsyncMock()

    @property
    def status(self):
        return self._status

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def mock_response():
    return MockResponse(status=200)


@pytest.fixture
def sdk():
    return LuminoSDK("test-api-key", "https://api.test.com/v1")
