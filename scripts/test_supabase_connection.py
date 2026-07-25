#!/usr/bin/env python3
"""
Test script to verify Supabase connection and read tables.
This script tests the connection to your Supabase database and reads the tables.
"""

import os
import sys
from dotenv import load_dotenv
from supabase import create_client, Client
import json

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def test_connection():
    """Test connection to Supabase."""
    print("=" * 60)
    print("Testing Supabase Connection")
    print("=" * 60)
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ ERROR: Missing Supabase credentials in .env")
        print(f"   SUPABASE_URL: {'✓' if SUPABASE_URL else '✗'}")
        print(f"   SUPABASE_KEY: {'✓' if SUPABASE_KEY else '✗'}")
        return False
    
    print(f"✓ SUPABASE_URL: {SUPABASE_URL}")
    print(f"✓ SUPABASE_KEY: {'*' * len(SUPABASE_KEY)}")
    
    try:
        # Create client
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✓ Supabase client created successfully")
        
        # Test connection by fetching a table
        print("\n" + "-" * 60)
        print("Testing whatsapp_messages table...")
        print("-" * 60)
        
        response = supabase.table("whatsapp_messages").select("*").limit(5).execute()
        
        if response.data:
            print(f"✓ Found {len(response.data)} messages")
            for i, row in enumerate(response.data[:3], 1):
                print(f"\n  Message {i}:")
                print(f"    ID: {row.get('id')}")
                print(f"    Telefone: {row.get('telefone')}")
                print(f"    Nome: {row.get('nome')}")
                print(f"    Mensagem: {row.get('mensagem')}")
                print(f"    Custo Total: {row.get('custo_total')}")
                print(f"    Moeda: {row.get('moeda')}")
        else:
            print("⚠ No messages found in whatsapp_messages table")
        
        # Test meta_pricing table
        print("\n" + "-" * 60)
        print("Testing meta_pricing table...")
        print("-" * 60)
        
        pricing_response = supabase.table("meta_pricing").select("*").execute()
        
        if pricing_response.data:
            print(f"✓ Found {len(pricing_response.data)} pricing entries")
            for i, row in enumerate(pricing_response.data[:3], 1):
                print(f"\n  Pricing {i}:")
                print(f"    ID: {row.get('id')}")
                print(f"    Country Code: {row.get('country_code')}")
                print(f"    Message Category: {row.get('message_category')}")
                print(f"    Cost per Message: {row.get('cost_per_message')}")
                print(f"    Currency: {row.get('currency')}")
        else:
            print("⚠ No pricing entries found in meta_pricing table")
        
        # Get table statistics
        print("\n" + "-" * 60)
        print("Table Statistics")
        print("-" * 60)
        
        # Count messages
        count_response = supabase.table("whatsapp_messages").select("id", count="exact").execute()
        total_messages = count_response.count if hasattr(count_response, 'count') else len(count_response.data) if count_response.data else 0
        print(f"Total messages: {total_messages}")
        
        # Count messages with cost
        with_cost_response = supabase.table("whatsapp_messages").select("id", count="exact").not_.is_("custo_total", None).execute()
        with_cost = with_cost_response.count if hasattr(with_cost_response, 'count') else len(with_cost_response.data) if with_cost_response.data else 0
        print(f"Messages with cost: {with_cost}")
        
        # Count messages without cost
        without_cost = total_messages - with_cost
        print(f"Messages without cost: {without_cost}")
        
        # Count pricing entries
        pricing_count_response = supabase.table("meta_pricing").select("id", count="exact").execute()
        total_pricing = pricing_count_response.count if hasattr(pricing_count_response, 'count') else len(pricing_count_response.data) if pricing_count_response.data else 0
        print(f"Total pricing entries: {total_pricing}")
        
        print("\n" + "=" * 60)
        print("✓ Supabase connection test completed successfully!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("\n" + "=" * 60)
        print("✗ Supabase connection test failed")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
