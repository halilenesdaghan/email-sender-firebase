import os
from pathlib import Path
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Proje kök dizini
BASE_DIR = Path(__file__).resolve().parent.parent

# Firebase ayarları
FIREBASE_CONFIG_PATH = os.getenv('FIREBASE_CONFIG_PATH', 'config/firebase_config.json')
FIREBASE_CONFIG_FULL_PATH = BASE_DIR / FIREBASE_CONFIG_PATH

# E-posta ayarları
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
GMAIL_CREDENTIALS_PATH = os.getenv('GMAIL_CREDENTIALS_PATH', 'config/gmail_credentials.json')
GMAIL_CREDENTIALS_FULL_PATH = BASE_DIR / GMAIL_CREDENTIALS_PATH

# Uygulama ayarları
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
APP_ENV = os.getenv('APP_ENV', 'development')

# E-posta içeriği
EMAIL_SUBJECT = "Başlık: Merhaba Dünya"
EMAIL_BODY = "Merhaba Dünya!"