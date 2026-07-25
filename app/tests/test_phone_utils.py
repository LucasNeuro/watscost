"""
Tests for phone utility functions.
"""

import pytest
from app.utils.phone_utils import (
    normalize_phone_number,
    extract_country_code,
    validate_phone_number
)


class TestPhoneUtils:
    """Test cases for phone utility functions."""
    
    def test_normalize_phone_number_valid(self):
        """Test normalizing valid phone numbers."""
        # Already in international format
        assert normalize_phone_number("+5511999999999") == "+5511999999999"
        
        # With spaces and dashes
        assert normalize_phone_number("+55 11 99999-9999") == "+5511999999999"
        
        # Without + but valid
        assert normalize_phone_number("5511999999999") == "+5511999999999"
    
    def test_normalize_phone_number_invalid(self):
        """Test normalizing invalid phone numbers."""
        # Local format (starts with 0)
        with pytest.raises(ValueError):
            normalize_phone_number("011999999999")
        
        # Too short
        with pytest.raises(ValueError):
            normalize_phone_number("123")
    
    def test_extract_country_code(self):
        """Test extracting country codes."""
        assert extract_country_code("+5511999999999") == "55"
        assert extract_country_code("+14155552671") == "1"
        assert extract_country_code("+442071234567") == "44"
        assert extract_country_code("5511999999999") == "55"
    
    def test_extract_country_code_invalid(self):
        """Test extracting country codes from invalid numbers."""
        with pytest.raises(ValueError):
            extract_country_code("123")
        
        with pytest.raises(ValueError):
            extract_country_code("invalid")
    
    def test_validate_phone_number(self):
        """Test phone number validation."""
        # Valid numbers
        assert validate_phone_number("+5511999999999") == True
        assert validate_phone_number("+14155552671") == True
        assert validate_phone_number("+442071234567") == True
        
        # Invalid numbers
        assert validate_phone_number("123") == False
        assert validate_phone_number("011999999999") == False
        assert validate_phone_number("invalid") == False
        assert validate_phone_number("+123") == False  # Too short
