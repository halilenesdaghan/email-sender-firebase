import pytest
from utils.validators import is_valid_email, sanitize_email, validate_email_input

class TestValidators:
    """E-posta doğrulayıcı testleri"""
    
    def test_valid_emails(self):
        """Geçerli e-posta adresleri"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "firstname+lastname@example.com",
            "email@subdomain.example.com",
            "1234567890@example.com",
            "email@example-one.com"
        ]
        
        for email in valid_emails:
            assert is_valid_email(email) is True
    
    def test_invalid_emails(self):
        """Geçersiz e-posta adresleri"""
        invalid_emails = [
            "plainaddress",
            "@no-local.com",
            "missing-at-sign.com",
            "missing@domain",
            "two@@example.com",
            "dotdot..@example.com",
            "spaces in@example.com"
        ]
        
        for email in invalid_emails:
            assert is_valid_email(email) is False
    
    def test_sanitize_email(self):
        """E-posta temizleme"""
        assert sanitize_email("  TEST@EXAMPLE.COM  ") == "test@example.com"
        assert sanitize_email("User@Domain.Com") == "user@domain.com"
        assert sanitize_email("email@test.com") == "email@test.com"
    
    def test_validate_email_input(self):
        """E-posta girişi doğrulama"""
        # Boş giriş
        is_valid, message = validate_email_input("")
        assert is_valid is False
        assert "boş olamaz" in message
        
        # Geçersiz format
        is_valid, message = validate_email_input("invalid-email")
        assert is_valid is False
        assert "Geçersiz" in message
        
        # Geçerli e-posta
        is_valid, email = validate_email_input("  TEST@EXAMPLE.COM  ")
        assert is_valid is True
        assert email == "test@example.com"