"""
Utility functions for phone number handling.
"""

import re
from typing import Optional


def normalize_phone_number(phone: str) -> str:
    """
    Normalize a phone number to international format.
    
    Args:
        phone: The phone number to normalize
        
    Returns:
        str: Normalized phone number in international format
        
    Raises:
        ValueError: If phone number cannot be normalized
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # If it starts with 0 (local format), we can't normalize without country code
    if digits.startswith('0'):
        raise ValueError(
            f"Phone number {phone} appears to be in local format. "
            "Please provide in international format (e.g., +5511999999999)"
        )
    
    # If it doesn't start with a country code, we can't normalize
    if len(digits) < 8:  # Minimum reasonable length for a phone number
        raise ValueError(f"Invalid phone number length: {phone}")
    
    # If it already starts with +, return as is
    if phone.startswith('+'):
        return phone
    
    # Otherwise, assume it's already in international format without +
    return f"+{digits}"


def extract_country_code(phone: str) -> str:
    """
    Extract country code from a phone number.
    
    Args:
        phone: Phone number in international format
        
    Returns:
        str: The country code
        
    Raises:
        ValueError: If phone number format is invalid
    """
    # Normalize the phone number first
    normalized = phone
    if not phone.startswith('+'):
        normalized = normalize_phone_number(phone)
    
    # Extract digits after +
    match = re.match(r'\+(\d{1,4})', normalized)
    if not match:
        raise ValueError(f"Invalid phone number format: {phone}")
    
    return match.group(1)


def validate_phone_number(phone: str) -> bool:
    """
    Validate if a phone number is in valid international format.
    
    Args:
        phone: The phone number to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        # Should start with + followed by digits
        pattern = r'^\+\d{8,15}$'
        return bool(re.match(pattern, phone))
    except:
        return False
