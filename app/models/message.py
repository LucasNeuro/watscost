"""
WhatsApp message model adapted to real Supabase schema.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime
import uuid


class WhatsAppMessage(BaseModel):
    """Model representing a WhatsApp message from Supabase (real schema)."""
    
    id: uuid.UUID = Field(description="Unique identifier (UUID)")
    data: datetime = Field(description="Message timestamp")
    mensagem: Dict[str, Any] = Field(description="Message content as JSONB")
    nome: str = Field(description="Contact name")
    telefone: str = Field(description="Phone number")
    custo_total: Optional[float] = Field(default=None, description="Total cost")
    moeda: str = Field(default="BRL", description="Currency")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "data": "2024-01-15T10:30:00Z",
                "mensagem": {"text": "Your verification code is 123456"},
                "nome": "John Doe",
                "telefone": "+5511999999999",
                "custo_total": 0.015,
                "moeda": "BRL"
            }
        }


class WhatsAppMessageResponse(BaseModel):
    """Model for WhatsApp message response with calculated cost."""
    
    id: uuid.UUID
    data: datetime
    mensagem: Dict[str, Any]
    nome: str
    telefone: str
    custo_total: Optional[float]
    moeda: str
    categoria: Optional[str] = Field(default=None, description="Message category")
    country_code: Optional[str] = Field(default=None, description="Extracted country code")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "data": "2024-01-15T10:30:00Z",
                "mensagem": {"text": "Your verification code is 123456"},
                "nome": "John Doe",
                "telefone": "+5511999999999",
                "custo_total": 0.015,
                "moeda": "BRL",
                "categoria": "authentication",
                "country_code": "55"
            }
        }


class WhatsAppMessageCreate(BaseModel):
    """Model for creating a new WhatsApp message."""
    
    data: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    mensagem: Dict[str, Any] = Field(description="Message content as JSONB")
    nome: str = Field(description="Contact name")
    telefone: str = Field(description="Phone number")
    custo_total: Optional[float] = Field(default=None, description="Total cost")
    moeda: str = Field(default="BRL", description="Currency")
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": "2024-01-15T10:30:00Z",
                "mensagem": {"text": "Your verification code is 123456"},
                "nome": "John Doe",
                "telefone": "+5511999999999",
                "custo_total": None,
                "moeda": "BRL"
            }
        }
