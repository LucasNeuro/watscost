"""
Pricing model adapted to real Supabase schema.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
import uuid


class MetaPricing(BaseModel):
    """Model representing pricing information from meta_pricing table (real schema)."""
    
    id: uuid.UUID = Field(description="Unique identifier (UUID)")
    country_code: str = Field(description="Country code (e.g., '55' for Brazil)")
    message_category: str = Field(description="Message category (service, utility, authentication, marketing)")
    cost_per_message: float = Field(description="Cost per message")
    currency: str = Field(default="BRL", description="Currency")
    effective_date: date = Field(description="Effective date of this pricing")
    end_date: Optional[date] = Field(default=None, description="End date of this pricing")
    is_template: bool = Field(default=False, description="Is this a template?")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Update timestamp")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "country_code": "55",
                "message_category": "authentication",
                "cost_per_message": 0.015,
                "currency": "BRL",
                "effective_date": "2024-01-01",
                "end_date": None,
                "is_template": False,
                "notes": "Brazil authentication messages",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z"
            }
        }


class PricingResponse(BaseModel):
    """Model for pricing response."""
    
    country_code: str
    message_category: str
    cost_per_message: float
    currency: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "country_code": "55",
                "message_category": "authentication",
                "cost_per_message": 0.015,
                "currency": "BRL"
            }
        }
