# src/main.py (Revize Edilmiş Tam Hali)
import argparse
from colorama import Fore, Style, init
from src.firebase_client import FirebaseClient
from utils.validators import is_valid_email
from utils.logger import setup_logger

# Colorama'yı ve Logger'ı başlat
init(autoreset=True)
logger = setup_logger(__name__)

def main():
    """
    Komut satırından e-posta alıcısını alıp Firestore'a görev ekleyen ana fonksiyon.
    """
    parser = argparse.ArgumentParser(
        description="Bir alıcıya e-posta göndermek için Firestore'a bir görev ekler."
    )
    parser.add_argument(
        "--recipient",
        type=str,
        required=True,
        help="E-postanın gönderileceği alıcı adresi.",
    )
    
    args = parser.parse_args()
    recipient_email = args.recipient

    if not is_valid_email(recipient_email):
        logger.error(f"Geçersiz e-posta adresi: {recipient_email}")
        print(f"{Fore.RED}Hata: Girdiğiniz e-posta adresi geçersiz.{Style.RESET_ALL}")
        return

    try:
        logger.info(f"'{recipient_email}' adresine e-posta göndermek için görev oluşturuluyor...")
        
        # Firebase istemcisini oluştur
        firebase_client = FirebaseClient()
        
        # Gönderilecek e-posta içeriği
        subject = "Başlık: Merhaba Dünya"
        body = "Merhaba Dünya!"
        
        # Görevi Firestore'a ekle
        task_id = firebase_client.add_email_task(recipient_email, subject, body)
        
        if task_id:
            success_message = f"Görev başarıyla oluşturuldu. Takip ID: {task_id}"
            logger.info(success_message)
            print(f"{Fore.GREEN}✅ {success_message}{Style.RESET_ALL}")
            
    except Exception as e:
        error_message = f"Ana işlem sırasında beklenmedik bir hata oluştu: {e}"
        logger.critical(error_message)
        print(f"{Fore.RED}❌ Hata: İşlem gerçekleştirilemedi. Detaylar için logları kontrol edin.{Style.RESET_ALL}")

if __name__ == "__main__":
    # İnteraktif menü yerine doğrudan komut satırı argümanlarını kullanıyoruz
    main()