import firebase_admin
from firebase_admin import credentials, firestore, auth
from pathlib import Path
from config.settings import FIREBASE_CONFIG_FULL_PATH
from utils.logger import setup_logger

logger = setup_logger(__name__)

class FirebaseClient:
    """Firebase işlemleri için client sınıfı"""
    
    def __init__(self):
        self._app = None
        self._db = None
        
    def initialize(self):
        """Firebase'i başlat"""
        try:
            if not self._app:
                # Servis hesabı kimlik bilgilerini yükle
                if not Path(FIREBASE_CONFIG_FULL_PATH).exists():
                    raise FileNotFoundError(
                        f"Firebase config dosyası bulunamadı: {FIREBASE_CONFIG_FULL_PATH}"
                    )
                
                cred = credentials.Certificate(str(FIREBASE_CONFIG_FULL_PATH))
                self._app = firebase_admin.initialize_app(cred)
                self._db = firestore.client()
                
                logger.info("Firebase başarıyla başlatıldı")
                
        except Exception as e:
            logger.error(f"Firebase başlatma hatası: {str(e)}")
            raise
    
    def add_email_to_queue(self, email_data: dict):
        """
        E-posta gönderme görevini Firestore'daki 'emails' koleksiyonuna ekler.

        Args:
            email_data (dict): E-posta bilgilerini içeren sözlük.
        """
        if not self._db:
            logger.error("Firestore bağlantısı yok. Önce initialize() çağrılmalı.")
            raise ConnectionError("Firestore bağlantısı kurulamadı.")
        
        try:
            # 'emails' koleksiyonuna yeni bir doküman olarak ekle
            self._db.collection('emails').add(email_data)  # DÜZELTME: self.db yerine self._db
            logger.info(f"E-posta görevi '{email_data['to']}' için Firestore'a eklendi.")
        except Exception as e:
            logger.error(f"E-posta görevi Firestore'a eklenirken hata: {str(e)}")
            raise

    def log_email_activity(self, recipient: str, status: str, error: str = None):
        """
        E-posta gönderim aktivitesini Firebase'e logla
        
        Args:
            recipient (str): Alıcı e-posta adresi
            status (str): Gönderim durumu (success/failed)
            error (str, optional): Hata mesajı
        """
        try:
            doc_ref = self._db.collection('email_logs').document()
            doc_ref.set({
                'recipient': recipient,
                'subject': 'Başlık: Merhaba Dünya',
                'status': status,
                'error': error,
                'timestamp': firestore.SERVER_TIMESTAMP,
                'sender': 'system'
            })
            logger.info(f"E-posta aktivitesi loglandı: {recipient} - {status}")
            
        except Exception as e:
            logger.error(f"Firebase log hatası: {str(e)}")
    
    def get_email_history(self, limit: int = 10):
        """
        Son gönderilen e-postaların geçmişini getir
        
        Args:
            limit (int): Getirilecek kayıt sayısı
            
        Returns:
            list: E-posta log kayıtları
        """
        try:
            docs = (self._db.collection('email_logs')
                    .order_by('timestamp', direction=firestore.Query.DESCENDING)
                    .limit(limit)
                    .stream())
            
            history = []
            for doc in docs:
                data = doc.to_dict()
                history.append(data)
                
            return history
            
        except Exception as e:
            logger.error(f"E-posta geçmişi getirme hatası: {str(e)}")
            return []
    
    def close(self):
        """Firebase bağlantısını kapat"""
        if self._app:
            firebase_admin.delete_app(self._app)
            self._app = None
            self._db = None
            logger.info("Firebase bağlantısı kapatıldı")

# Singleton instance
firebase_client = FirebaseClient()