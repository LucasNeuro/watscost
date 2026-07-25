"""
Supabase database connection and client.
"""

from supabase import create_client, Client
from app.core.config import settings


def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance.
    
    Returns:
        Client: Supabase client configured with URL and API key.
    """
    return create_client(
        supabase_url=settings.supabase_url,
        supabase_key=settings.supabase_key
    )


# Global Supabase client instance
supabase_client = get_supabase_client()
