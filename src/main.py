#!/usr/bin/env python3
"""
E-posta Gönderici - Firebase Entegrasyonlu
Terminal üzerinden e-posta gönderme uygulaması
"""

import sys
import argparse
from colorama import Fore, Style, init

from utils.logger import setup_logger
from utils.validators import validate_email_input
from src.firebase_client import firebase_client
from src.email_service import email_service

# Colorama'yı başlat
init(autoreset=True)

# Logger
logger = setup_logger(__name__)

def print_banner():
    """Uygulama başlık banner'ı"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════╗
║      📧 E-POSTA GÖNDERİCİ v1.0 📧       ║
║         Firebase Entegrasyonlu           ║
╚══════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def print_success(message: str):
    """Başarı mesajı yazdır"""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")

def print_error(message: str):
    """Hata mesajı yazdır"""
    print(f"{Fore.RED}❌ {message}{Style.RESET_ALL}")

def print_info(message: str):
    """Bilgi mesajı yazdır"""
    print(f"{Fore.YELLOW}ℹ️  {message}{Style.RESET_ALL}")

def send_email_interactive():
    """İnteraktif modda e-posta gönder"""
    print_info("E-posta adresi girin (çıkmak için 'q' yazın):")
    
    while True:
        try:
            # Kullanıcıdan e-posta al
            email_input = input(f"{Fore.CYAN}📮 E-posta adresi: {Style.RESET_ALL}").strip()
            
            # Çıkış kontrolü
            if email_input.lower() in ['q', 'quit', 'exit']:
                print_info("Uygulama kapatılıyor...")
                break
            
            # E-posta doğrulama
            is_valid, result = validate_email_input(email_input)
            
            if not is_valid:
                print_error(result)
                continue
            
            # Temizlenmiş e-posta adresi
            recipient = result
            
            print_info(f"E-posta gönderiliyor: {recipient}")
            
            # E-postayı gönder
            if email_service.send_email(recipient):
                print_success(f"E-posta başarıyla gönderildi: {recipient}")
                print_info(f"Konu: {Fore.WHITE}Başlık: Merhaba Dünya{Style.RESET_ALL}")
                print_info(f"İçerik: {Fore.WHITE}Merhaba Dünya!{Style.RESET_ALL}")
            else:
                print_error("E-posta gönderilemedi! Lütfen logları kontrol edin.")
            
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n")
            print_info("Uygulama kullanıcı tarafından durduruldu.")
            break
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {str(e)}")
            print_error(f"Beklenmeyen hata: {str(e)}")

def send_email_direct(recipient: str):
    """Doğrudan e-posta gönder"""
    # E-posta doğrulama
    is_valid, result = validate_email_input(recipient)
    
    if not is_valid:
        print_error(result)
        return False
    
    # Temizlenmiş e-posta adresi
    recipient = result
    
    print_info(f"E-posta gönderiliyor: {recipient}")
    
    # E-postayı gönder
    if email_service.send_email(recipient):
        print_success(f"E-posta başarıyla gönderildi: {recipient}")
        return True
    else:
        print_error("E-posta gönderilemedi! Lütfen logları kontrol edin.")
        return False

def show_history(limit: int = 10):
    """E-posta gönderim geçmişini göster"""
    print_info(f"Son {limit} e-posta gönderimi:")
    print("-" * 70)
    
    history = firebase_client.get_email_history(limit)
    
    if not history:
        print_info("Henüz e-posta gönderim kaydı yok.")
        return
    
    for i, log in enumerate(history, 1):
        status_icon = "✅" if log.get('status') == 'success' else "❌"
        print(f"{i}. {status_icon} {log.get('recipient', 'N/A')} - {log.get('timestamp', 'N/A')}")
        if log.get('error'):
            print(f"   {Fore.RED}Hata: {log.get('error')}{Style.RESET_ALL}")

def main():
    """Ana fonksiyon"""
    parser = argparse.ArgumentParser(
        description='Firebase entegrasyonlu e-posta gönderici'
    )
    
    parser.add_argument(
        '-e', '--email',
        type=str,
        help='Doğrudan e-posta gönder'
    )
    
    parser.add_argument(
        '-H', '--history',
        action='store_true',
        help='E-posta gönderim geçmişini göster'
    )
    
    parser.add_argument(
        '-l', '--limit',
        type=int,
        default=10,
        help='Geçmiş kayıt limiti (varsayılan: 10)'
    )
    
    args = parser.parse_args()
    
    try:
        # Banner'ı göster
        print_banner()
        
        # Firebase'i başlat
        print_info("Firebase bağlantısı kuruluyor...")
        firebase_client.initialize()
        print_success("Firebase bağlantısı kuruldu!")
        
        # Komut satırı argümanlarına göre işlem yap
        if args.history:
            show_history(args.limit)
        elif args.email:
            send_email_direct(args.email)
        else:
            # İnteraktif mod
            send_email_interactive()
            
    except Exception as e:
        logger.error(f"Uygulama hatası: {str(e)}")
        print_error(f"Uygulama hatası: {str(e)}")
        sys.exit(1)
    finally:
        # Firebase bağlantısını kapat
        firebase_client.close()
        print_info("İyi günler! 👋")

if __name__ == "__main__":
    main()