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
    
    async def add_computing_providers_batch(self, addresses: List[str]) -> Dict[str, Any]:
        """
        Add multiple computing providers to the whitelist in a batch.
        
        Args:
            addresses: List of computing provider addresses to whitelist
            
        Returns:
            Dictionary with operation results including transaction hash
        """
        payload = {"addresses": addresses}
        response = await self.http_client.post("/whitelist/computing-providers/batch", payload)
        return response


    async def remove_computing_providers_batch(self, addresses: List[str]) -> Dict[str, Any]:
        """
        Remove multiple computing providers from the whitelist in a batch.
        
        Args:
            addresses: List of computing provider addresses to remove
            
        Returns:
            Dictionary with operation results including transaction hash
        """
        payload = {"addresses": addresses}
        response = await self.http_client.delete("/whitelist/computing-providers/batch", json=payload)
        return response


@property
def whitelist(self) -> WhitelistClient:
    return WhitelistClient(self.http_client)