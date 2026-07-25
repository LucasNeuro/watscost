"""
Service for classifying WhatsApp messages using Mistral AI.
"""

import httpx
from typing import Optional
from app.core.config import settings
from app.schemas.message import MessageClassificationRequest, MessageClassificationResponse
from app.models.message import WhatsAppMessage


class MistralService:
    """Service to interact with Mistral AI API for message classification."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Mistral service with API key.
        
        Args:
            api_key: Mistral API key. If None, uses settings.mistral_api_key
        """
        self.api_key = api_key or settings.mistral_api_key
        self.base_url = "https://api.mistral.ai/v1"
        self.model = "mistral-tiny"  # Using tiny model for cost efficiency
        
    def _get_headers(self) -> dict:
        """Get headers for Mistral API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def classify_message(self, message: str) -> str:
        """
        Classify a WhatsApp message into one of the predefined categories.
        
        Args:
            message: The message content to classify
            
        Returns:
            str: The classified category (service, utility, authentication, marketing)
            
        Raises:
            ValueError: If classification fails or returns invalid category
            httpx.HTTPError: If there's an error calling the Mistral API
        """
        # Prepare the prompt for classification
        categories = settings.message_categories
        prompt = f"""Classify the following WhatsApp message into one of these categories: {', '.join(categories)}.

Message: "{message}"

Respond with ONLY the category name, nothing else. Do not add explanations or formatting.

Example:
- "Your verification code is 123456" -> authentication
- "Your order has been shipped" -> service
- "Your bill is due tomorrow" -> utility
- "Check out our new products" -> marketing

Category:"""
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.0,  # Low temperature for deterministic output
            "max_tokens": 50
        }
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._get_headers(),
                    json=payload
                )
                response.raise_for_status()
                
                # Extract the category from the response
                result = response.json()
                category = result["choices"][0]["message"]["content"].strip().lower()
                
                # Validate the category
                if category not in categories:
                    # If Mistral returns an invalid category, try to map it
                    category = self._map_category(category)
                
                if category not in categories:
                    raise ValueError(f"Invalid category returned: {category}. Expected one of: {categories}")
                
                return category
                
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError("Invalid Mistral API key")
            elif e.response.status_code == 429:
                raise ValueError("Mistral API rate limit exceeded")
            else:
                raise ValueError(f"Mistral API error: {e.response.text}")
        except Exception as e:
            raise ValueError(f"Failed to classify message: {str(e)}")
    
    def _map_category(self, category: str) -> str:
        """
        Map common alternative category names to our standard categories.
        
        Args:
            category: The category to map
            
        Returns:
            str: The mapped category
        """
        category_mapping = {
            "auth": "authentication",
            "authentication_code": "authentication",
            "verification": "authentication",
            "otp": "authentication",
            "2fa": "authentication",
            "service_message": "service",
            "customer_service": "service",
            "support": "service",
            "utility_message": "utility",
            "notification": "utility",
            "reminder": "utility",
            "bill": "utility",
            "payment": "utility",
            "ad": "marketing",
            "promotion": "marketing",
            "advertisement": "marketing",
            "promo": "marketing",
            "offer": "marketing"
        }
        
        return category_mapping.get(category, category)
    
    def classify_message_with_fallback(self, message: str) -> str:
        """
        Classify a message with fallback logic if Mistral fails.
        
        Args:
            message: The message content to classify
            
        Returns:
            str: The classified category
        """
        try:
            return self.classify_message(message)
        except Exception as e:
            # Fallback: use keyword-based classification
            return self._classify_with_keywords(message)
    
    def _classify_with_keywords(self, message: str) -> str:
        """
        Fallback classification using keyword matching.
        
        Args:
            message: The message content
            
        Returns:
            str: The classified category
        """
        message_lower = message.lower()
        
        # Authentication keywords
        auth_keywords = [
            "code", "verification", "verify", "otp", "password", "login", 
            "sign in", "sign up", "register", "authentication", "2fa",
            "confirmation", "confirm", "secure", "security"
        ]
        
        # Service keywords
        service_keywords = [
            "order", "shipment", "delivery", "tracking", "support",
            "help", "assistance", "customer service", "ticket", "status",
            "update", "notification", "alert"
        ]
        
        # Utility keywords
        utility_keywords = [
            "bill", "payment", "invoice", "due", "reminder", "balance",
            "account", "transaction", "receipt", "statement"
        ]
        
        # Marketing keywords
        marketing_keywords = [
            "promotion", "promo", "offer", "discount", "sale", "deal",
            "new", "product", "service", "check out", "visit", "buy",
            "purchase", "advertisement", "ad", "campaign"
        ]
        
        # Check for authentication
        if any(keyword in message_lower for keyword in auth_keywords):
            return "authentication"
        
        # Check for utility
        if any(keyword in message_lower for keyword in utility_keywords):
            return "utility"
        
        # Check for marketing
        if any(keyword in message_lower for keyword in marketing_keywords):
            return "marketing"
        
        # Default to service
        return "service"


# Global Mistral service instance
mistral_service = MistralService()
