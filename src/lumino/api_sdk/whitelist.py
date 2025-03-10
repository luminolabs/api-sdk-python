# Add to lumino/api_sdk/models.py
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr


class WhitelistRequestCreate(BaseModel):
    """
    Request model for creating a new whitelist request.
    """
    name: str
    email: EmailStr
    phone_number: str


class WhitelistRequestResponse(BaseModel):
    """
    Response model for whitelist request data.
    """
    id: str
    user_id: str
    name: str
    email: EmailStr
    phone_number: str
    is_whitelisted: bool
    has_signed_nda: bool
    created_at: str
    updated_at: str

class WhitelistClient:
    """
    Client for whitelist operations.
    """
    
    def __init__(self, http_client):
        self.http_client = http_client
    
    async def request_to_be_whitelisted(self, request: WhitelistRequestCreate) -> WhitelistRequestResponse:
        """
        Submit a new whitelist request.
        
        Args:
            request: The whitelist request data.
            
        Returns:
            The created whitelist request.
        """
        response = await self.http_client.post("/whitelist", request.dict())
        return WhitelistRequestResponse(**response)
    
    async def get_whitelist_status(self) -> WhitelistRequestResponse:
        """
        Get the current user's whitelist status.
        
        Returns:
            The whitelist status.
        """
        response = await self.http_client.get("/whitelist")
        return WhitelistRequestResponse(**response)


@property
def whitelist(self) -> WhitelistClient:
    return WhitelistClient(self.http_client)