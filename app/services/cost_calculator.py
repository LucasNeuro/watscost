"""
Service for calculating WhatsApp message costs (adapted to real schema).
"""

from typing import Optional, Tuple
from app.services.mistral_service import mistral_service
from app.services.supabase_service import supabase_service
from app.models.message import WhatsAppMessage, WhatsAppMessageResponse
from app.models.pricing import MetaPricing
from app.schemas.message import CostCalculationResponse


class CostCalculatorService:
    """Service to calculate costs for WhatsApp messages."""
    
    def __init__(self, mistral_service=None, supabase_service=None):
        """
        Initialize cost calculator service.
        
        Args:
            mistral_service: Mistral service instance
            supabase_service: Supabase service instance
        """
        self.mistral_service = mistral_service or mistral_service
        self.supabase_service = supabase_service or supabase_service
    
    def calculate_cost_for_message(self, message: WhatsAppMessage) -> Tuple[str, float, str]:
        """
        Calculate the cost for a single message.
        
        Args:
            message: The WhatsApp message to calculate cost for
            
        Returns:
            Tuple[str, float, str]: (category, cost_per_message, country_code)
            
        Raises:
            ValueError: If classification or pricing lookup fails
        """
        # Extract country code from phone number
        country_code = self.supabase_service.extract_country_code(message.telefone)
        
        # Get message text from JSONB
        message_text = self.supabase_service.get_message_text(message)
        
        # Classify the message
        category = self.mistral_service.classify_message_with_fallback(message_text)
        
        # Get pricing (using message_category instead of category)
        pricing = self.supabase_service.get_pricing(country_code, category)
        
        if pricing is None:
            raise ValueError(
                f"No pricing found for country_code={country_code}, category={category}. "
                f"Please add an entry to the meta_pricing table."
            )
        
        return category, pricing.cost_per_message, country_code
    
    def process_message(self, message_id: str) -> CostCalculationResponse:
        """
        Process a single message: classify, calculate cost, and update database.
        
        Args:
            message_id: The UUID of the message to process
            
        Returns:
            CostCalculationResponse: The processed message with cost information
            
        Raises:
            ValueError: If processing fails
        """
        # Get the message
        message = self.supabase_service.get_message_by_id(message_id)
        
        if message is None:
            raise ValueError(f"Message {message_id} not found")
        
        # Calculate cost
        category, cost_per_message, country_code = self.calculate_cost_for_message(message)
        
        # Calculate total cost (1 message * cost_per_message)
        custo_total = 1 * cost_per_message
        
        # Update the message in database
        updated_message = self.supabase_service.update_message_cost(
            message_id=str(message.id),
            categoria=category,
            custo_total=custo_total,
            country_code=country_code
        )
        
        return CostCalculationResponse(
            message_id=str(message.id),
            telefone=updated_message.telefone,
            categoria=category,
            country_code=country_code,
            cost_per_message=cost_per_message,
            custo_total=custo_total,
            currency=updated_message.moeda or "BRL"
        )
    
    def process_messages_batch(self, limit: int = 100) -> Tuple[int, float, list]:
        """
        Process multiple unprocessed messages in batch.
        
        Args:
            limit: Maximum number of messages to process
            
        Returns:
            Tuple[int, float, list]: (processed_count, total_cost, list of CostCalculationResponse)
        """
        # Get unprocessed messages
        messages = self.supabase_service.get_unprocessed_messages(limit=limit)
        
        processed_messages = []
        total_cost = 0.0
        processed_count = 0
        
        for message in messages:
            try:
                response = self.process_message(str(message.id))
                processed_messages.append(response)
                total_cost += response.custo_total
                processed_count += 1
            except Exception as e:
                # Log error but continue with other messages
                print(f"Error processing message {message.id}: {str(e)}")
                continue
        
        return processed_count, total_cost, processed_messages


# Global cost calculator service instance
cost_calculator_service = CostCalculatorService()
