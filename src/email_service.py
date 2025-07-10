# src/email_service.py

from src.firebase_client import firebase_client
from utils.logger import setup_logger
from config.settings import SENDER_EMAIL

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
            # Trigger Email extension'ının standart formatı
            email_data = {
                'to': [to],  # Liste olarak
                'from': SENDER_EMAIL,  # Gönderen adresi ekleyelim
                'message': {
                    'subject': subject,
                    'text': message_text,
                    'html': f'''
                    <html>
                        <body>
                            <h2>{subject}</h2>
                            <p>{message_text}</p>
                            <hr>
                            <p><small>Bu e-posta Firebase Email Extension ile gönderilmiştir.</small></p>
                        </body>
                    </html>
                    '''
                },
                # Extension'ın işlemesi için gerekli olabilecek ek alanlar
                'delivery': {
                    'startTime': None,  # Hemen gönder
                    'endTime': None,
                    'leaseExpireTime': None,
                    'attempts': 0,
                    'error': None,
                    'state': 'PENDING'  # Extension bu alanı kullanıyor olabilir
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