import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config.settings import (
    SENDER_EMAIL, 
    GMAIL_CREDENTIALS_FULL_PATH,
    EMAIL_SUBJECT,
    EMAIL_BODY
)
from utils.logger import setup_logger
from src.firebase_client import firebase_client

logger = setup_logger(__name__)

# Gmail API kapsamları
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class EmailService:
    """Gmail API kullanarak e-posta gönderme servisi"""
    
    def __init__(self):
        self.service = None
        self.creds = None
        
    def authenticate(self):
        """Gmail API kimlik doğrulaması"""
        try:
            token_path = Path('config/token.pickle')
            
            # Token varsa yükle
            if token_path.exists():
                with open(token_path, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # Token yoksa veya geçersizse yenile
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    if not Path(GMAIL_CREDENTIALS_FULL_PATH).exists():
                        raise FileNotFoundError(
                            f"Gmail credentials dosyası bulunamadı: {GMAIL_CREDENTIALS_FULL_PATH}"
                        )
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(GMAIL_CREDENTIALS_FULL_PATH), SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                
                # Token'ı kaydet
                with open(token_path, 'wb') as token:
                    pickle.dump(self.creds, token)
            
            # Gmail servisini oluştur
            self.service = build('gmail', 'v1', credentials=self.creds)
            logger.info("Gmail API kimlik doğrulaması başarılı")
            
        except Exception as e:
            logger.error(f"Gmail API kimlik doğrulama hatası: {str(e)}")
            raise
    
    def create_message(self, recipient: str) -> dict:
        """
        E-posta mesajı oluştur
        
        Args:
            recipient (str): Alıcı e-posta adresi
            
        Returns:
            dict: Gmail API için hazır mesaj
        """
        message = MIMEMultipart()
        message['to'] = recipient
        message['from'] = SENDER_EMAIL
        message['subject'] = EMAIL_SUBJECT
        
        # Mesaj gövdesi
        body = MIMEText(EMAIL_BODY, 'plain', 'utf-8')
        message.attach(body)
        
        # Base64 encode
        raw_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode('utf-8')
        
        return {'raw': raw_message}
    
    def send_email(self, recipient: str) -> bool:
        """
        E-posta gönder
        
        Args:
            recipient (str): Alıcı e-posta adresi
            
        Returns:
            bool: Başarılı ise True, değilse False
        """
        try:
            # Kimlik doğrulaması yapılmamışsa yap
            if not self.service:
                self.authenticate()
            
            # Mesajı oluştur
            message = self.create_message(recipient)
            
            # E-postayı gönder
            result = self.service.users().messages().send(
                userId='me',
                body=message
            ).execute()
            
            logger.info(f"E-posta başarıyla gönderildi: {recipient}")
            logger.debug(f"Gmail API Response: {result}")
            
            # Firebase'e başarılı gönderimi logla
            firebase_client.log_email_activity(recipient, 'success')
            
            return True
            
        except HttpError as e:
            error_msg = f"Gmail API hatası: {str(e)}"
            logger.error(error_msg)
            
            # Firebase'e başarısız gönderimi logla
            firebase_client.log_email_activity(recipient, 'failed', error_msg)
            
            return False
            
        except Exception as e:
            error_msg = f"E-posta gönderim hatası: {str(e)}"
            logger.error(error_msg)
            
            # Firebase'e başarısız gönderimi logla
            firebase_client.log_email_activity(recipient, 'failed', error_msg)
            
            return False

# Singleton instance
email_service = EmailService()