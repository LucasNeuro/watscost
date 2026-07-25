"""
Pricing model for WhatsApp message costs.
"""

from pydantic import BaseModel, Field
from typing import Optional


class MetaPricing(BaseModel):
    """Model representing pricing information from meta_pricing table."""
    
    id: int = Field(description="Unique identifier for the pricing entry")
    country_code: str = Field(description="Country code (e.g., '55' for Brazil)")
    category: str = Field(description="Message category (service, utility, authentication, marketing)")
    cost_per_message: float = Field(description="Cost per message in USD")
    currency: str = Field(default="USD", description="Currency of the cost")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "country_code": "55",
                "category": "authentication",
                "cost_per_message": 0.015,
                "currency": "USD"
            }
        }


class PricingResponse(BaseModel):
    """Model for pricing response."""
    
    country_code: str
    category: str
    cost_per_message: float
    currency: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "country_code": "55",
                "category": "authentication",
                "cost_per_message": 0.015,
                "currency": "USD"
            }
        }
