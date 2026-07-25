"""
Application configuration using Pydantic Settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    app_name: str = Field(default="WhatsApp Cost Calculator API")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    
    # Server Configuration
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    
    # Supabase Configuration
    supabase_url: str = Field(default="")
    supabase_key: str = Field(default="")
    
    # Mistral Configuration
    mistral_api_key: str = Field(default="")
    
    # Message Classification Categories
    message_categories: list = Field(default=[
        "service", "utility", "authentication", "marketing"
    ])
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
