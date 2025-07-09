# src/email_service.py

from src.firebase_client import firebase_client
from utils.logger import setup_logger

logger = setup_logger(__name__)

class EmailService:
    """
    Bu servis, e-posta gönderme görevlerini doğrudan göndermek yerine
    Firebase Firestore'daki 'emails' koleksiyonuna ekler.
    Asıl gönderim işlemini buluttaki 'Trigger Email' eklentisi yapar.
    """
    def send_email(self, to: str, subject: str, message_text: str) -> bool:
        """
        E-posta verisini Firestore kuyruğuna ekler.
        
        Args:
            to (str): Alıcı e-posta adresi.
            subject (str): E-posta konusu.
            message_text (str): E-posta metni.

        Returns:
            bool: Kuyruğa ekleme başarılıysa True, değilse False.
        """
        try:
            # Trigger Email eklentisinin beklediği formatta bir veri yapısı oluştur
            email_data = {
                'to': [to],  # Eklenti, 'to' alanını bir liste olarak bekler
                'message': {
                    'subject': subject,
                    'text': message_text,
                    'html': f'<p>{message_text}</p>'  # Basit bir HTML versiyonu da ekleyelim
                }
            }
            firebase_client.add_email_to_queue(email_data)
            logger.info(f"'{to}' adresine e-posta gönderim görevi başarıyla kuyruğa eklendi.")
            return True
        except Exception as e:
            logger.error(f"E-posta görevi Firestore'a eklenirken hata oluştu: {e}")
            return False

# Servisten bir örnek (instance) oluşturalım ki diğer dosyalardan kolayca erişilebilsin
email_service = EmailService()