"""
Service for analyzing WhatsApp messages from Supabase and calculating costs.
This service reads from the real Supabase tables and processes them.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date
from app.services.supabase_service import supabase_service
from app.services.mistral_service import mistral_service
from app.models.message import WhatsAppMessage
from app.models.pricing import MetaPricing
import uuid


class AnalysisService:
    """Service to analyze WhatsApp messages and calculate costs."""
    
    def __init__(self):
        """Initialize analysis service."""
        self.supabase = supabase_service
        self.mistral = mistral_service
    
    def get_all_messages(self, limit: int = 1000) -> List[WhatsAppMessage]:
        """
        Get all messages from Supabase.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List[WhatsAppMessage]: All messages from whatsapp_messages table
        """
        try:
            response = self.supabase.client.table("whatsapp_messages") \
                .select("*") \
                .limit(limit) \
                .execute()
            
            messages = [WhatsAppMessage(**row) for row in response.data]
            return messages
        except Exception as e:
            raise ValueError(f"Failed to fetch messages: {str(e)}")
    
    def get_messages_without_cost(self, limit: int = 1000) -> List[WhatsAppMessage]:
        """
        Get messages that don't have custo_total calculated.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List[WhatsAppMessage]: Messages without custo_total
        """
        try:
            response = self.supabase.client.table("whatsapp_messages") \
                .select("*") \
                .is_("custo_total", None) \
                .limit(limit) \
                .execute()
            
            messages = [WhatsAppMessage(**row) for row in response.data]
            return messages
        except Exception as e:
            raise ValueError(f"Failed to fetch messages without cost: {str(e)}")
    
    def get_all_pricing(self) -> List[MetaPricing]:
        """
        Get all pricing entries from meta_pricing table.
        
        Returns:
            List[MetaPricing]: All pricing entries
        """
        return self.supabase.get_all_pricing()
    
    def get_active_pricing(self) -> List[MetaPricing]:
        """
        Get only active pricing entries (where end_date is null or in the future).
        
        Returns:
            List[MetaPricing]: Active pricing entries
        """
        try:
            today = date.today().isoformat()
            response = self.supabase.client.table("meta_pricing") \
                .select("*") \
                .or_(f"end_date.is.null,end_date.gte.{today}") \
                .execute()
            
            return [MetaPricing(**row) for row in response.data]
        except Exception as e:
            raise ValueError(f"Failed to fetch active pricing: {str(e)}")
    
    def analyze_message(self, message: WhatsAppMessage) -> Dict[str, Any]:
        """
        Analyze a single message: extract text, classify, and find pricing.
        
        Args:
            message: The WhatsApp message to analyze
            
        Returns:
            Dict: Analysis result with category, cost, and metadata
        """
        # Extract country code from phone
        try:
            country_code = self.supabase.extract_country_code(message.telefone)
        except:
            country_code = "unknown"
        
        # Extract message text from JSONB
        message_text = self.supabase.get_message_text(message)
        
        # Classify the message
        try:
            category = self.mistral.classify_message_with_fallback(message_text)
        except Exception as e:
            category = "service"  # Fallback to service
            print(f"Classification failed for message {message.id}: {str(e)}")
        
        # Find pricing
        pricing = None
        try:
            pricing = self.supabase.get_pricing(country_code, category)
        except:
            pass
        
        # If no pricing found for specific category, try to find any pricing for country
        if not pricing:
            try:
                response = self.supabase.client.table("meta_pricing") \
                    .select("*") \
                    .eq("country_code", country_code) \
                    .limit(1) \
                    .execute()
                if response.data:
                    pricing = MetaPricing(**response.data[0])
                    category = pricing.message_category  # Use the category from pricing
            except:
                pass
        
        # Calculate cost
        cost_per_message = pricing.cost_per_message if pricing else 0.0
        custo_total = 1 * cost_per_message
        
        return {
            "message_id": str(message.id),
            "telefone": message.telefone,
            "nome": message.nome,
            "message_text": message_text,
            "country_code": country_code,
            "category": category,
            "cost_per_message": cost_per_message,
            "custo_total": custo_total,
            "currency": pricing.currency if pricing else "BRL",
            "has_pricing": pricing is not None,
            "pricing_id": str(pricing.id) if pricing else None
        }
    
    def analyze_all_messages(self, limit: int = 1000) -> Dict[str, Any]:
        """
        Analyze all messages from Supabase.
        
        Args:
            limit: Maximum number of messages to analyze
            
        Returns:
            Dict: Complete analysis report
        """
        messages = self.get_all_messages(limit=limit)
        
        results = []
        total_cost = 0.0
        messages_with_cost = 0
        messages_without_cost = 0
        messages_without_pricing = 0
        categories = {}
        countries = {}
        
        for message in messages:
            try:
                analysis = self.analyze_message(message)
                results.append(analysis)
                
                # Update statistics
                if message.custo_total is not None:
                    messages_with_cost += 1
                else:
                    messages_without_cost += 1
                
                if not analysis["has_pricing"]:
                    messages_without_pricing += 1
                
                total_cost += analysis["custo_total"]
                
                # Update category stats
                if analysis["category"] not in categories:
                    categories[analysis["category"]] = {"count": 0, "cost": 0.0}
                categories[analysis["category"]]["count"] += 1
                categories[analysis["category"]]["cost"] += analysis["custo_total"]
                
                # Update country stats
                if analysis["country_code"] not in countries:
                    countries[analysis["country_code"]] = {"count": 0, "cost": 0.0}
                countries[analysis["country_code"]]["count"] += 1
                countries[analysis["country_code"]]["cost"] += analysis["custo_total"]
                
            except Exception as e:
                print(f"Error analyzing message {message.id}: {str(e)}")
                continue
        
        return {
            "total_messages": len(messages),
            "messages_analyzed": len(results),
            "messages_with_cost": messages_with_cost,
            "messages_without_cost": messages_without_cost,
            "messages_without_pricing": messages_without_pricing,
            "total_cost": total_cost,
            "categories": categories,
            "countries": countries,
            "results": results
        }
    
    def process_and_update_messages(self, limit: int = 100) -> Dict[str, Any]:
        """
        Process messages without cost and update them in Supabase.
        
        Args:
            limit: Maximum number of messages to process
            
        Returns:
            Dict: Processing report
        """
        messages = self.get_messages_without_cost(limit=limit)
        
        processed = []
        updated = []
        errors = []
        total_cost = 0.0
        
        for message in messages:
            try:
                # Analyze the message
                analysis = self.analyze_message(message)
                processed.append(analysis)
                
                # Only update if we have pricing
                if analysis["has_pricing"]:
                    try:
                        # Update the message in Supabase
                        update_response = self.supabase.client.table("whatsapp_messages") \
                            .update({
                                "custo_total": analysis["custo_total"],
                                "moeda": analysis["currency"]
                            }) \
                            .eq("id", str(message.id)) \
                            .select("*") \
                            .execute()
                        
                        if update_response.data:
                            updated.append({
                                "message_id": str(message.id),
                                "custo_total": analysis["custo_total"],
                                "category": analysis["category"],
                                "country_code": analysis["country_code"]
                            })
                            total_cost += analysis["custo_total"]
                        else:
                            errors.append({
                                "message_id": str(message.id),
                                "error": "Update failed"
                            })
                    except Exception as e:
                        errors.append({
                            "message_id": str(message.id),
                            "error": str(e)
                        })
                else:
                    errors.append({
                        "message_id": str(message.id),
                        "error": "No pricing found"
                    })
                    
            except Exception as e:
                errors.append({
                    "message_id": str(message.id) if hasattr(message, 'id') else "unknown",
                    "error": str(e)
                })
        
        return {
            "total_messages": len(messages),
            "processed": len(processed),
            "updated": len(updated),
            "errors": len(errors),
            "total_cost": total_cost,
            "updated_messages": updated,
            "errors": errors
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about messages and costs.
        
        Returns:
            Dict: Statistics report
        """
        try:
            # Get message count
            messages_response = self.supabase.client.table("whatsapp_messages") \
                .select("id", count="exact") \
                .execute()
            
            total_messages = messages_response.count if hasattr(messages_response, 'count') else len(messages_response.data) if messages_response.data else 0
            
            # Get messages with cost
            with_cost_response = self.supabase.client.table("whatsapp_messages") \
                .select("id", count="exact") \
                .not_.is_("custo_total", None) \
                .execute()
            
            with_cost = with_cost_response.count if hasattr(with_cost_response, 'count') else len(with_cost_response.data) if with_cost_response.data else 0
            
            # Get messages without cost
            without_cost = total_messages - with_cost
            
            # Get total cost
            total_cost_response = self.supabase.client.table("whatsapp_messages") \
                .select("custo_total") \
                .not_.is_("custo_total", None) \
                .execute()
            
            total_cost = sum(float(row["custo_total"]) for row in total_cost_response.data) if total_cost_response.data else 0.0
            
            # Get pricing count
            pricing_response = self.supabase.client.table("meta_pricing") \
                .select("id", count="exact") \
                .execute()
            
            total_pricing = pricing_response.count if hasattr(pricing_response, 'count') else len(pricing_response.data) if pricing_response.data else 0
            
            return {
                "total_messages": total_messages,
                "messages_with_cost": with_cost,
                "messages_without_cost": without_cost,
                "total_cost": total_cost,
                "total_pricing_entries": total_pricing,
                "currency": "BRL"
            }
        except Exception as e:
            raise ValueError(f"Failed to get statistics: {str(e)}")


# Global analysis service instance
analysis_service = AnalysisService()
