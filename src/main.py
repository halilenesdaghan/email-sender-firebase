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
        email_address = input("📮 E-posta adresi: ").strip()
        if email_address.lower() == 'q':
            print_info("Uygulamadan çıkılıyor.")
            break
        if validate_email_input(email_address):
            print_info(f"E-posta görevi kuyruğa ekleniyor: {email_address}")
            success = email_service.send_email(email_address, "Test E-postası", "Bu bir test e-postasıdır.")
            if success:
                # Log mesajını ve durumunu güncelle
                firebase_client.log_email_activity(email_address, 'queued')
                print_success("E-posta başarıyla kuyruğa eklendi!")
            else:
                # Log mesajını ve durumunu güncelle
                firebase_client.log_email_activity(email_address, 'queue_failed')
                print_error("E-posta kuyruğa eklenemedi! Lütfen logları kontrol edin.")
        print("-" * 50)

def check_email_queue():
    """Firestore'daki emails koleksiyonunu kontrol et"""
    print_info("Firestore'daki e-posta kuyruğu kontrol ediliyor...")
    
    try:
        # firebase_client'a bu metodu ekleyelim
        emails = firebase_client._db.collection('emails').limit(5).stream()
        
        email_count = 0
        for doc in emails:
            email_count += 1
            data = doc.to_dict()
            print(f"\n📧 Doküman ID: {doc.id}")
            print(f"   To: {data.get('to', 'N/A')}")
            print(f"   State: {data.get('delivery', {}).get('state', 'N/A')}")
            print(f"   Error: {data.get('delivery', {}).get('error', 'None')}")
            
            # Extension tarafından eklenen alanları kontrol et
            if 'delivery' in data and 'info' in data['delivery']:
                print(f"   Info: {data['delivery']['info']}")
        
        if email_count == 0:
            print_info("Kuyrukta bekleyen e-posta bulunamadı.")
        else:
            print_info(f"Toplam {email_count} e-posta bulundu.")
            
    except Exception as e:
        print_error(f"Kuyruk kontrol hatası: {str(e)}")

def send_email_direct(email: str):
    """Doğrudan e-posta gönder"""
    if validate_email_input(email):
        print_info(f"E-posta görevi kuyruğa ekleniyor: {email}")
        success = email_service.send_email(email, "Test E-postası", "Bu bir test e-postasıdır.")
        if success:
            # Log mesajını ve durumunu güncelle
            firebase_client.log_email_activity(email, 'queued')
            print_success("E-posta başarıyla kuyruğa eklendi!")
        else:
            # Log mesajını ve durumunu güncelle
            firebase_client.log_email_activity(email, 'queue_failed')
            print_error("E-posta kuyruğa eklenemedi! Lütfen logları kontrol edin.")

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