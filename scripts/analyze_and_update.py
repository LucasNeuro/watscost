#!/usr/bin/env python3
"""
Script to analyze and update WhatsApp messages from Supabase.
This script:
1. Reads all messages from whatsapp_messages table
2. Classifies each message using Mistral AI
3. Finds pricing based on country code and category
4. Updates messages with calculated costs
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client
from mistralai.client import MistralClient
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

# Load environment variables
load_dotenv()

# Get credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")


def extract_country_code(phone: str) -> str:
    """Extract country code from phone number."""
    if not phone:
        return "unknown"
    
    # Remove non-digit characters except +
    cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    if cleaned.startswith('+'):
        # Extract digits after +
        country_code = cleaned[1:]
        # Get first 1-3 digits
        return country_code[:3] if len(country_code) > 3 else country_code
    
    return "unknown"


def get_message_text(mensagem: Any) -> str:
    """Extract text from JSONB mensagem field."""
    if isinstance(mensagem, dict):
        return mensagem.get("text", "") or str(mensagem)
    elif isinstance(mensagem, str):
        return mensagem
    else:
        return str(mensagem)


def classify_message(message_text: str, api_key: str) -> str:
    """Classify message using Mistral AI."""
    categories = ["service", "utility", "authentication", "marketing"]
    
    # Fallback classification using keywords
    message_lower = message_text.lower()
    
    # Authentication keywords
    auth_keywords = [
        "code", "verification", "verify", "otp", "password", "login", 
        "sign in", "sign up", "register", "authentication", "2fa",
        "confirmation", "confirm", "secure", "security", "código",
        "verificação", "senha", "autenticação"
    ]
    
    # Service keywords
    service_keywords = [
        "order", "shipment", "delivery", "tracking", "support",
        "help", "assistance", "customer service", "ticket", "status",
        "update", "notification", "alert", "pedido", "entrega",
        "rastreamento", "suporte", "atendimento"
    ]
    
    # Utility keywords
    utility_keywords = [
        "bill", "payment", "invoice", "due", "reminder", "balance",
        "account", "transaction", "receipt", "statement", "conta",
        "pagamento", "fatura", "saldo", "lembrete"
    ]
    
    # Marketing keywords
    marketing_keywords = [
        "promotion", "promo", "offer", "discount", "sale", "deal",
        "new", "product", "service", "check out", "visit", "buy",
        "purchase", "advertisement", "ad", "campaign", "oferta",
        "promoção", "desconto", "novo", "produto"
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


def get_pricing(supabase: any, country_code: str, category: str) -> Optional[Dict]:
    """Get pricing from meta_pricing table."""
    try:
        response = supabase.table("meta_pricing") \
            .select("*") \
            .eq("country_code", country_code) \
            .eq("message_category", category) \
            .single() \
            .execute()
        
        return response.data if response.data else None
    except:
        return None


def analyze_and_update(limit: int = 10):
    """Main function to analyze and update messages."""
    print("=" * 70)
    print("WhatsApp Message Analysis and Cost Update Script")
    print("=" * 70)
    
    # Validate credentials
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ ERROR: Missing Supabase credentials")
        return False
    
    if not MISTRAL_API_KEY:
        print("⚠ WARNING: Mistral API key not provided, using keyword fallback")
    
    print(f"\n✓ Supabase URL: {SUPABASE_URL}")
    print(f"✓ Supabase Key: {'*' * len(SUPABASE_KEY)}")
    print(f"✓ Mistral API Key: {'*' * len(MISTRAL_API_KEY) if MISTRAL_API_KEY else 'Not provided'}")
    
    try:
        # Create clients
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("\n✓ Connected to Supabase")
        
        # Get messages without cost
        print(f"\n📋 Fetching {limit} messages without cost...")
        response = supabase.table("whatsapp_messages") \
            .select("*") \
            .is_("custo_total", None) \
            .limit(limit) \
            .execute()
        
        messages = response.data if response.data else []
        print(f"✓ Found {len(messages)} messages to process")
        
        if not messages:
            print("\n⚠ No messages without cost found")
            return True
        
        # Process each message
        processed = 0
        updated = 0
        errors = 0
        total_cost = 0.0
        
        print("\n" + "-" * 70)
        print("Processing Messages")
        print("-" * 70)
        
        for i, message in enumerate(messages, 1):
            try:
                message_id = message.get("id")
                telefone = message.get("telefone", "")
                nome = message.get("nome", "")
                mensagem = message.get("mensagem", {})
                
                print(f"\n{i}. Message ID: {message_id}")
                print(f"   Telefone: {telefone}")
                print(f"   Nome: {nome}")
                
                # Extract country code
                country_code = extract_country_code(telefone)
                print(f"   Country Code: {country_code}")
                
                # Extract message text
                message_text = get_message_text(mensagem)
                print(f"   Message: {message_text[:50]}...")
                
                # Classify message
                category = classify_message(message_text, MISTRAL_API_KEY)
                print(f"   Category: {category}")
                
                # Get pricing
                pricing = get_pricing(supabase, country_code, category)
                if pricing:
                    cost_per_message = float(pricing.get("cost_per_message", 0))
                    currency = pricing.get("currency", "BRL")
                    custo_total = 1 * cost_per_message
                    
                    print(f"   Cost per Message: {cost_per_message} {currency}")
                    print(f"   Total Cost: {custo_total} {currency}")
                    
                    # Update message in Supabase
                    try:
                        update_response = supabase.table("whatsapp_messages") \
                            .update({
                                "custo_total": custo_total,
                                "moeda": currency
                            }) \
                            .eq("id", message_id) \
                            .execute()
                        
                        if update_response.data:
                            updated += 1
                            total_cost += custo_total
                            print(f"   ✓ Updated successfully")
                        else:
                            print(f"   ⚠ Update failed")
                            errors += 1
                    except Exception as e:
                        print(f"   ❌ Update error: {str(e)}")
                        errors += 1
                else:
                    print(f"   ⚠ No pricing found for country={country_code}, category={category}")
                    errors += 1
                
                processed += 1
                
            except Exception as e:
                print(f"\n❌ Error processing message {i}: {str(e)}")
                errors += 1
        
        # Print summary
        print("\n" + "=" * 70)
        print("Processing Summary")
        print("=" * 70)
        print(f"Total messages processed: {processed}")
        print(f"Messages updated: {updated}")
        print(f"Errors: {errors}")
        print(f"Total cost calculated: {total_cost:.2f} BRL")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False


if __name__ == "__main__":
    # Parse command line arguments
    limit = 10
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except:
            print(f"Invalid limit: {sys.argv[1]}")
            sys.exit(1)
    
    success = analyze_and_update(limit=limit)
    sys.exit(0 if success else 1)
