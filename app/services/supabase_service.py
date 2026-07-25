"""
Service for interacting with Supabase database.
"""

from typing import List, Optional, Dict, Any
from app.core.database import supabase_client
from app.models.message import WhatsAppMessage, WhatsAppMessageResponse
from app.models.pricing import MetaPricing
from app.core.config import settings
from app.utils.phone_utils import extract_country_code as phone_extract_country_code


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
                # Add country_code if not present
                if not message.country_code:
                    message.country_code = self.extract_country_code(message.telefone)
                messages.append(message)
            
            return messages
            
        except Exception as e:
            raise ValueError(f"Failed to fetch unprocessed messages: {str(e)}")
    
    def get_message_by_id(self, message_id: int) -> Optional[WhatsAppMessage]:
        """
        Get a specific message by its ID.
        
        Args:
            message_id: The ID of the message to retrieve
            
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
                message = WhatsAppMessage(**response.data)
                if not message.country_code:
                    message.country_code = self.extract_country_code(message.telefone)
                return message
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
            response = self.client.table("meta_pricing") \
                .select("*") \
                .eq("country_code", country_code) \
                .eq("category", category) \
                .single() \
                .execute()
            
            if response.data:
                return MetaPricing(**response.data)
            return None
            
        except Exception as e:
            raise ValueError(f"Failed to fetch pricing for country_code={country_code}, category={category}: {str(e)}")
    
    def update_message_cost(self, message_id: int, categoria: str, custo_total: float, country_code: str) -> WhatsAppMessageResponse:
        """
        Update a message with its calculated cost and category.
        
        Args:
            message_id: The ID of the message to update
            categoria: The classified category
            custo_total: The calculated total cost
            country_code: The extracted country code
            
        Returns:
            WhatsAppMessageResponse: The updated message
            
        Raises:
            ValueError: If the update fails
        """
        try:
            response = self.client.table("whatsapp_messages") \
                .update({
                    "categoria": categoria,
                    "custo_total": custo_total,
                    "country_code": country_code
                }) \
                .eq("id", message_id) \
                .select("*") \
                .single() \
                .execute()
            
            if response.data:
                return WhatsAppMessageResponse(**response.data)
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
            # Add country_code if phone number is provided
            if "telefone" in message_data and "country_code" not in message_data:
                message_data["country_code"] = self.extract_country_code(message_data["telefone"])
            
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


# Global Supabase service instance
supabase_service = SupabaseService()
