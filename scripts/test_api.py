#!/usr/bin/env python3
"""
Test script for WhatsApp Cost Calculator API.
This script tests the API endpoints locally.
"""

import httpx
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.core.config import settings


def test_api():
    """Test the API endpoints."""
    
    # Create a test client
    client = httpx.Client(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver"
    )
    
    print("=" * 60)
    print("Testing WhatsApp Cost Calculator API")
    print("=" * 60)
    
    try:
        # Test 1: Root endpoint
        print("\n[TEST 1] Testing root endpoint...")
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Root endpoint working: {data['name']} v{data['version']}")
        
        # Test 2: Health check
        print("\n[TEST 2] Testing health check...")
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        print(f"✓ Health check: {data['status']}")
        
        # Test 3: Classification endpoint (mock test - will fail without Mistral API key)
        print("\n[TEST 3] Testing classification endpoint...")
        try:
            response = client.post(
                "/classify/",
                json={"message": "Your verification code is 123456"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Classification: {data['category']}")
            else:
                print(f"⚠ Classification endpoint requires Mistral API key: {response.json()}")
        except Exception as e:
            print(f"⚠ Classification test skipped (Mistral API not configured): {str(e)}")
        
        # Test 4: Pricing endpoint (mock test - will fail without Supabase)
        print("\n[TEST 4] Testing pricing endpoint...")
        try:
            response = client.get("/pricing/")
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Pricing endpoint working: {len(data)} entries")
            else:
                print(f"⚠ Pricing endpoint requires Supabase: {response.json()}")
        except Exception as e:
            print(f"⚠ Pricing test skipped (Supabase not configured): {str(e)}")
        
        # Test 5: Messages endpoint (mock test)
        print("\n[TEST 5] Testing messages endpoint...")
        try:
            response = client.get("/messages/unprocessed")
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Messages endpoint working: {len(data)} unprocessed messages")
            else:
                print(f"⚠ Messages endpoint requires Supabase: {response.json()}")
        except Exception as e:
            print(f"⚠ Messages test skipped (Supabase not configured): {str(e)}")
        
        print("\n" + "=" * 60)
        print("API tests completed!")
        print("=" * 60)
        
        # Show configuration
        print("\nCurrent Configuration:")
        print(f"  App Name: {settings.app_name}")
        print(f"  App Version: {settings.app_version}")
        print(f"  Debug Mode: {settings.debug}")
        print(f"  Supabase URL: {'***' if settings.supabase_url else 'Not configured'}")
        print(f"  Mistral API Key: {'***' if settings.mistral_api_key else 'Not configured'}")
        
        print("\nTo run the API locally:")
        print("  uvicorn app.main:app --reload")
        print("\nThen access the docs at:")
        print("  http://localhost:8000/docs")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {str(e)}")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {str(e)}")
        return False
    finally:
        client.close()
    
    return True


if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
