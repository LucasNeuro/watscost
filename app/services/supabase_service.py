"""
Service for interacting with Supabase database (adapted to real schema).
"""

from typing import List, Optional, Dict, Any
from app.core.database import supabase_client
from app.models.message import WhatsAppMessage, WhatsAppMessageResponse
from app.models.pricing import MetaPricing
from app.core.config import settings
from app.utils.phone_utils import extract_country_code as phone_extract_country_code
import re


class SupabaseService:
    """Service to interact with Supabase for WhatsApp messages and pricing."""
    
    def __init__(self, client=None):
        """
        Initialize Supabase service.
        
        Args:
            client: Supabase client. If None, uses the global client.
        """
        self.client = client or supabase_client
    
    def extract_country_code(self, phone_number: str) -> str:
        """
        Extract country code from a phone number.
        
        Args:
            phone_number: Phone number in international format (e.g., +5511999999999)
            
        Returns:
            str: The country code (e.g., "55")
            
        Raises:
            ValueError: If phone number format is invalid
        """
        return phone_extract_country_code(phone_number)
    
    def get_unprocessed_messages(self, limit: int = 100) -> List[WhatsAppMessage]:
        """
        Get messages that haven't had their cost calculated yet.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List[WhatsAppMessage]: List of unprocessed messages
        """
        try:
            # Query messages where custo_total is NULL
            response = self.client.table("whatsapp_messages") \
                .select("*") \
                .is_("custo_total", None) \
                .limit(limit) \
                .execute()
            
            messages = []
            for row in response.data:
                message = WhatsAppMessage(**row)
                messages.append(message)
            
            return messages
            
        except Exception as e:
            raise ValueError(f"Failed to fetch unprocessed messages: {str(e)}")
    
    def get_message_by_id(self, message_id: str) -> Optional[WhatsAppMessage]:
        """
        Get a specific message by its ID.
        
        Args:
            message_id: The UUID of the message to retrieve
            
        Returns:
            Optional[WhatsAppMessage]: The message if found, None otherwise
        """
        try:
            response = self.client.table("whatsapp_messages") \
                .select("*") \
                .eq("id", message_id) \
                .single() \
                .execute()
            
            if response.data:
                return WhatsAppMessage(**response.data)
            return None
            
        except Exception as e:
            raise ValueError(f"Failed to fetch message {message_id}: {str(e)}")
    
    def get_pricing(self, country_code: str, category: str) -> Optional[MetaPricing]:
        """
        Get pricing information for a specific country and category.
        
        Args:
            country_code: The country code (e.g., "55")
            category: The message category (service, utility, authentication, marketing)
            
        Returns:
            Optional[MetaPricing]: Pricing information if found, None otherwise
        """
        try:
            # Note: The real schema uses 'message_category' instead of 'category'
            response = self.client.table("meta_pricing") \
                .select("*") \
                .eq("country_code", country_code) \
                .eq("message_category", category) \
                .single() \
                .execute()
            
            if response.data:
                return MetaPricing(**response.data)
            return None
            
        except Exception as e:
            raise ValueError(f"Failed to fetch pricing for country_code={country_code}, category={category}: {str(e)}")
    
    def update_message_cost(self, message_id: str, categoria: str, custo_total: float, country_code: str) -> WhatsAppMessageResponse:
        """
        Update a message with its calculated cost and category.
        
        Args:
            message_id: The UUID of the message to update
            categoria: The classified category
            custo_total: The calculated total cost
            country_code: The extracted country code
            
        Returns:
            WhatsAppMessageResponse: The updated message
            
        Raises:
            ValueError: If the update fails
        """
        try:
            # Get the current message to preserve existing fields
            current_message = self.get_message_by_id(message_id)
            if not current_message:
                raise ValueError(f"Message {message_id} not found")
            
            # Update only the fields we need
            response = self.client.table("whatsapp_messages") \
                .update({
                    "custo_total": custo_total,
                    "moeda": "BRL"
                }) \
                .eq("id", message_id) \
                .select("*") \
                .single() \
                .execute()
            
            if response.data:
                # Create response with additional fields
                message_data = response.data
                message_data["categoria"] = categoria
                message_data["country_code"] = country_code
                return WhatsAppMessageResponse(**message_data)
            else:
                raise ValueError(f"Message {message_id} not found or update failed")
            
        except Exception as e:
            raise ValueError(f"Failed to update message {message_id}: {str(e)}")
    
    def create_message(self, message_data: Dict[str, Any]) -> WhatsAppMessageResponse:
        """
        Create a new WhatsApp message in the database.
        
        Args:
            message_data: Dictionary containing message data
            
        Returns:
            WhatsAppMessageResponse: The created message
        """
        try:
            response = self.client.table("whatsapp_messages") \
                .insert(message_data) \
                .select("*") \
                .single() \
                .execute()
            
            if response.data:
                return WhatsAppMessageResponse(**response.data)
            else:
                raise ValueError("Failed to create message")
            
        except Exception as e:
            raise ValueError(f"Failed to create message: {str(e)}")
    
    def get_all_pricing(self) -> List[MetaPricing]:
        """
        Get all pricing entries from meta_pricing table.
        
        Returns:
            List[MetaPricing]: All pricing entries
        """
        try:
            response = self.client.table("meta_pricing") \
                .select("*") \
                .execute()
            
            return [MetaPricing(**row) for row in response.data]
            
        except Exception as e:
            raise ValueError(f"Failed to fetch all pricing: {str(e)}")
    
    def get_message_text(self, message: WhatsAppMessage) -> str:
        """
        Extract text from message JSONB field.
        
        Args:
            message: The WhatsApp message
            
        Returns:
            str: The message text content
        """
        if isinstance(message.mensagem, dict):
            return message.mensagem.get("text", "")
        elif isinstance(message.mensagem, str):
            return message.mensagem
        else:
            return str(message.mensagem)


# Global Supabase service instance
supabase_service = SupabaseService()
