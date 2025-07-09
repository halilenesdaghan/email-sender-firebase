import re
from email_validator import validate_email, EmailNotValidError
from utils.logger import setup_logger

logger = setup_logger(__name__)

def is_valid_email(email: str) -> bool:
    """
    E-posta adresinin geçerliliğini kontrol eder
    
    Args:
        email (str): Kontrol edilecek e-posta adresi
        
    Returns:
        bool: Geçerli ise True, değilse False
    """
    try:
        # email-validator kütüphanesi ile doğrulama
        validation = validate_email(email, check_deliverability=False)
        email = validation.email
        logger.debug(f"E-posta adresi geçerli: {email}")
        return True
    except EmailNotValidError as e:
        logger.error(f"Geçersiz e-posta adresi: {email} - Hata: {str(e)}")
        return False

def sanitize_email(email: str) -> str:
    """
    E-posta adresini temizler (boşluklar, büyük/küçük harf)
    
    Args:
        email (str): Temizlenecek e-posta adresi
        
    Returns:
        str: Temizlenmiş e-posta adresi
    """
    return email.strip().lower()

def validate_email_input(email: str) -> tuple[bool, str]:
    """
    E-posta girişini doğrular ve temizler
    
    Args:
        email (str): Kullanıcıdan alınan e-posta adresi
        
    Returns:
        tuple[bool, str]: (Geçerli mi, Temizlenmiş e-posta veya hata mesajı)
    """
    if not email:
        return False, "E-posta adresi boş olamaz!"
    
    # Temizle
    email = sanitize_email(email)
    
    # Doğrula
    if not is_valid_email(email):
        return False, "Geçersiz e-posta formatı!"
    
    return True, email