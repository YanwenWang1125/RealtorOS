"""
Client Pydantic schemas for API validation.

This module defines Pydantic schemas for client-related API requests
and responses in the RealtorOS system.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr

class ClientBase(BaseModel):
    """Base client schema with common fields."""
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    property_address: str = Field(..., min_length=1, max_length=200)
    property_type: str = Field(..., regex=r'^(residential|commercial|land|other)$')
    stage: str = Field(..., regex=r'^(lead|negotiating|under_contract|closed|lost)$')
    notes: Optional[str] = Field(None, max_length=1000)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

class ClientCreate(ClientBase):
    """Schema for creating a new client."""
    pass

class ClientUpdate(BaseModel):
    """Schema for updating a client."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    property_address: Optional[str] = Field(None, min_length=1, max_length=200)
    property_type: Optional[str] = Field(None, regex=r'^(residential|commercial|land|other)$')
    stage: Optional[str] = Field(None, regex=r'^(lead|negotiating|under_contract|closed|lost)$')
    notes: Optional[str] = Field(None, max_length=1000)
    custom_fields: Optional[Dict[str, Any]] = None

class ClientResponse(ClientBase):
    """Schema for client API responses."""
    id: str
    created_at: datetime
    updated_at: datetime
    last_contacted: Optional[datetime] = None

    class Config:
        from_attributes = True
