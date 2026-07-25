"""
Schemas for message-related requests and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class MessageClassificationRequest(BaseModel):
    """Request schema for message classification."""
    
    message: str = Field(description="Message content to classify")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Your verification code is 123456"
            }
        }


class MessageClassificationResponse(BaseModel):
    """Response schema for message classification."""
    
    message: str
    category: str
    confidence: Optional[float] = Field(default=None, description="Confidence score (0-1)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Your verification code is 123456",
                "category": "authentication",
                "confidence": 0.95
            }
        }


class CostCalculationRequest(BaseModel):
    """Request schema for cost calculation."""
    
    message_id: int = Field(description="ID of the message to calculate cost for")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message_id": 1
            }
        }


class CostCalculationResponse(BaseModel):
    """Response schema for cost calculation."""
    
    message_id: int
    telefone: str
    categoria: str
    country_code: str
    cost_per_message: float
    custo_total: float
    currency: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "message_id": 1,
                "telefone": "+5511999999999",
                "categoria": "authentication",
                "country_code": "55",
                "cost_per_message": 0.015,
                "custo_total": 0.015,
                "currency": "USD"
            }
        }


class BatchProcessRequest(BaseModel):
    """Request schema for batch processing."""
    
    limit: Optional[int] = Field(default=100, ge=1, le=1000, description="Maximum number of messages to process")
    
    class Config:
        json_schema_extra = {
            "example": {
                "limit": 100
            }
        }


class BatchProcessResponse(BaseModel):
    """Response schema for batch processing."""
    
    processed_count: int = Field(description="Number of messages processed")
    total_cost: float = Field(description="Total cost of all processed messages")
    messages: List[CostCalculationResponse] = Field(description="List of processed messages with costs")
    
    class Config:
        json_schema_extra = {
            "example": {
                "processed_count": 5,
                "total_cost": 0.075,
                "messages": [
                    {
                        "message_id": 1,
                        "telefone": "+5511999999999",
                        "categoria": "authentication",
                        "country_code": "55",
                        "cost_per_message": 0.015,
                        "custo_total": 0.015,
                        "currency": "USD"
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Standard error response schema."""
    
    error: str = Field(description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    message_id: Optional[int] = Field(default=None, description="ID of the message that caused the error")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Pricing not found",
                "detail": "No pricing entry found for country_code=55 and category=authentication",
                "message_id": 1
            }
        }
