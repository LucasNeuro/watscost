"""
WhatsApp message model.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WhatsAppMessage(BaseModel):
    """Model representing a WhatsApp message from Supabase."""
    
    id: int = Field(description="Unique identifier for the message")
    telefone: str = Field(description="Phone number in international format (e.g., +5511999999999)")
    mensagem: str = Field(description="Message content")
    data_envio: datetime = Field(description="Message send date and time")
    status: str = Field(default="sent", description="Message status")
    categoria: Optional[str] = Field(default=None, description="Message category (service, utility, authentication, marketing)")
    custo_total: Optional[float] = Field(default=None, description="Total cost of the message")
    country_code: Optional[str] = Field(default=None, description="Extracted country code from phone number")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "telefone": "+5511999999999",
                "mensagem": "Your verification code is 123456",
                "data_envio": "2024-01-15T10:30:00Z",
                "status": "sent",
                "categoria": "authentication",
                "custo_total": 0.015,
                "country_code": "55"
            }
        }


class WhatsAppMessageCreate(BaseModel):
    """Model for creating a new WhatsApp message."""
    
    telefone: str = Field(description="Phone number in international format")
    mensagem: str = Field(description="Message content")
    data_envio: datetime = Field(default_factory=datetime.utcnow, description="Message send date and time")
    status: str = Field(default="sent", description="Message status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "telefone": "+5511999999999",
                "mensagem": "Your verification code is 123456",
                "data_envio": "2024-01-15T10:30:00Z",
                "status": "sent"
            }
        }


class WhatsAppMessageResponse(BaseModel):
    """Model for WhatsApp message response with calculated cost."""
    
    id: int
    telefone: str
    mensagem: str
    data_envio: datetime
    status: str
    categoria: str
    custo_total: float
    country_code: str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "telefone": "+5511999999999",
                "mensagem": "Your verification code is 123456",
                "data_envio": "2024-01-15T10:30:00Z",
                "status": "sent",
                "categoria": "authentication",
                "custo_total": 0.015,
                "country_code": "55"
            }
        }
